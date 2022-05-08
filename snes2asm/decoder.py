# -*- coding: utf-8 -*-

from snes2asm.disassembler import Instruction
from snes2asm.tile import Decode8bppTile, Decode4bppTile, Decode2bppTile
from snes2asm.bitmap import BitmapIndex

class Decoder:
	def __init__(self, label=None, start=0, end=0):
		self.label = label
		self.start = start
		self.end = end
		self.files = []

	def name(self):
		return "%s%06x-%06x" % (self.__name__, self.start, self.end)

	def decode(self, cart):
		show_label = self.label != None
		for y in range(self.start, self.end, 16):
			line = '.db ' + ', '.join(("$%02X" % x) for x in cart[y : min(y+16, self.end)])
			if show_label:
				yield (y, Instruction(line, preamble=self.label+":"))
				show_label = False
			else:
				yield (y, Instruction(line))

	def add_file(self, name, data):
		self.files.append((name, data))

class Headers(Decoder):
	def __init__(self, start, end):
		Decoder.__init__(self, label="Headers", start=start, end=end)

	def decode(self, cart):
		yield (self.start, Instruction('; Auto-generated headers', preamble=self.label+":"))

class BinaryDecoder(Decoder):
	def __init__(self, label, start, end):
		Decoder.__init__(self, label, start, end)

	def decode(self, cart):
		data = []
		for y in range(self.start, self.end, 16):
			data.append('.db ' + ', '.join(("$%02X" % x) for x in cart[y : min(y+16, self.end)]))
		self.add_file("%s.inc" % self.label, "\n".join(data))
		yield (self.start, Instruction(".INCLUDE \"%s.inc\"" % self.label, preamble=self.label+":"))

class TextDecoder(Decoder):
	def __init__(self, label=None, start=0, end=0, pack=None):
		Decoder.__init__(self, label, start, end)
		self.pack = pack
		if self.pack != None:
			if type(self.pack) is not list:
				raise ValueError("TextDecoder: pack parameter is not an array")

	def decode(self, cart):
		if self.pack == None:
			string = ''.join( chr(x) for x in cart[self.start : self.end])
			line = '.db "%s"' % ansi_escape(string)
			yield (self.start, Instruction(line, preamble=self.label+":"))
		else:
			pos = self.start
			for (label, size) in self.pack:
				string = ''.join( chr(x) for x in cart[pos : pos + size])
				line = '.db "%s"' % ansi_escape(string)
				yield (pos, Instruction(line, preamble=label+":"))
				pos = pos + size

class PaletteDecoder(Decoder):
	def __init__(self, start, end, label=None):
		Decoder.__init__(self, label, start, end)

		if (self.end - self.start) & 0x1 != 0:
			raise ValueError("Palette start and end (0x%06X-0x%06X) do not align with 2-byte color entries" % (self.start, self.end))

	def decode(self, cart):
		# Output pal file
		file_name = "%s.pal" % self.label
		self.add_file(file_name, bytearray(cart[self.start:self.end]))

		lines = []
		for i in xrange(self.start, self.end, 2):
			bgr565  = cart[i] << 8 | cart[i+1]
			rgbcolor = (bgr565 & 0xf800) >> 8 | (bgr565 & 0x7e0) << 5 | (bgr565 & 0x1f) << 18
			lines.append("#%06X" % rgbcolor)

		self.add_file("%s.rgb" % self.label, "\n".join(lines) )

		yield (self.start, Instruction(".INCBIN \"%s\""% file_name, preamble=self.label+":"))

class GraphicDecoder(Decoder):
	def __init__(self, label, start, end, bit_depth=4, width=128, palette=None):
		Decoder.__init__(self, label, start, end)
		self.bit_depth = bit_depth
		self.width = width

		if self.width & 0x7 != 0:
			raise ValueError("Tile value width must be a multiple of 8")

		if self.bit_depth == 8:
			self.tile_decoder = Decode8bppTile
			self.tile_size = 64
		elif self.bit_depth == 2:
			self.tile_decoder = Decode2bppTile
			self.tile_size = 16
		else:
			self.tile_decoder = Decode4bppTile
			self.tile_size = 32

		if (self.end - self.start) % self.tile_size != 0:
			raise ValueError("Tile start and end (0x%06X-0x%06X) do not align with the %d-bit tile size" % (self.start, self.end, self.bit_depth))

	def palette(self):
		colors = 1 << self.bit_depth
		return [ (x << 10 | x << 18 | x << 2) for x in xrange(0, colors ) ]

	def decode(self, cart):
		# Output chr file
		file_name = "%s.chr" % self.label
		self.add_file(file_name, bytearray(cart[self.start:self.end]))

		# Output bitmap file
		tile_count = (self.end - self.start) / self.tile_size
		tiles_wide = self.width / 8
		height = (tile_count / tiles_wide) * 8
		if tile_count % tiles_wide != 0:
			height = height + 8

		bitmap = BitmapIndex(self.width, height, self.bit_depth, self.palette())

		tile_index = 0
		for i in xrange(self.start, self.end, self.tile_size):
			tile = self.tile_decoder(cart[i:i+self.tile_size])

			tile_x = (tile_index % tiles_wide) * 8
			tile_y = (tile_index / tiles_wide) * 8
			for y in xrange(0,8):
				for x in xrange(0,8):
					bitmap.setPixel(tile_x+x,tile_y+y, tile[y*8+x])
			tile_index = tile_index + 1

		self.add_file("%s.bmp" % self.label, bitmap.output())

		# Make binary chr file include
		yield (self.start, Instruction(".INCBIN \"%s\""% file_name, preamble=self.label+":"))

_ESCAPE_CHARS = {'\t': '\\t', '\n': '\\n', '\r': '\\r', '\x0b': '\\x0b', '\x0c': '\\x0c', '"': '\\"', '\x00': '\\' + '0'}

def ansi_escape(subject):
	return ''.join([ _ESCAPE_CHARS[c] if c in _ESCAPE_CHARS else c for c in subject])

