# -*- coding: utf-8 -*-

from snes2asm.disassembler import Instruction
from snes2asm.tile import Decode8bppTile, Decode4bppTile, Decode2bppTile
from snes2asm.bitmap import BitmapIndex

class Decoder:
	def __init__(self, label=None, start=0, end=0):
		self.label = label
		self.start = start
		self.end = end
		self.files = {}

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

	def no_data(self):
		return self.start == self.end

	def add_file(self, name, data):
		self.files[name] = data

class Headers(Decoder):
	def __init__(self, start, end):
		Decoder.__init__(self, label="Headers", start=start, end=end)

	def decode(self, cart):
		yield (self.start, Instruction('; Auto-generated headers', preamble=self.label+":"))

class BinaryDecoder(Decoder):
	def __init__(self, label, start, end):
		Decoder.__init__(self, label, start, end)

	def decode(self, cart):
		self.add_file("%s.bin" % self.label, bytearray(cart[self.start:self.end]))
		yield (self.start, Instruction(".INCBIN \"%s.bin\"" % self.label, preamble=self.label+":"))

class TextDecoder(Decoder):
	def __init__(self, label, start, end=0, pack=None, translation=None):
		# Calculate end from pack
		if end == 0 and pack != None:
			end = start + sum([x[1] for x in pack])
		Decoder.__init__(self, label, start, end)
		self.translation = translation
		self.pack = pack
		if self.pack != None:
			if type(self.pack) is not list:
				raise ValueError("TextDecoder: pack parameter is not an array")

	def decode(self, cart):
		if self.pack:
			pos = self.start
			for (label, size) in self.pack:
				end = pos + size
				output = self.text(cart[pos:end])
				if self.translation:
					yield (pos, Instruction('.STRINGMAP %s "%s"' % (self.translation.label, quote_escape(output)), preamble=label+":"))
				else:
					yield (pos, Instruction('.db "%s"' % quote_escape(output), preamble=label+":"))
				pos = end
		else:
			output = self.text(cart[self.start:self.end])
			if self.translation:
				yield (self.start, Instruction('.STRINGMAP %s "%s"' % (self.translation.label, quote_escape(output)), preamble=self.label+":"))
			else:
				yield (self.start, Instruction('.db "%s"' % quote_escape(output), preamble=self.label+":"))

	def text(self, input):
		if self.translation:
			output = []
			for char in input:
				if char in self.translation.table:
					output.append(self.translation.table[char])
				else:
					output.append(chr(char))
			return ansi_escape("".join(output))
		else:
			return ansi_escape(str(input))

class PaletteDecoder(Decoder):
	def __init__(self, start, end, label=None):
		Decoder.__init__(self, label, start, end)
		self.colors = []
		if (self.end - self.start) & 0x1 != 0:
			raise ValueError("Palette start and end (0x%06X-0x%06X) do not align with 2-byte color entries" % (self.start, self.end))

	def colorCount(self):
		return (self.end - self.start) / 2

	def decode(self, cart):
		# Output pal file
		file_name = "%s.pal" % self.label
		self.add_file(file_name, bytearray(cart[self.start:self.end]))

		lines = []
		for i in xrange(self.start, self.end, 2):
			bgr565 = cart[i] | cart[i+1] << 8
			rgbcolor = ((bgr565 & 0x7c00) >> 7 | (bgr565 & 0x3e0) << 6 | (bgr565 & 0x1f) << 19)
			self.colors.append(rgbcolor)
			lines.append("#%06X" % rgbcolor)

		self.add_file("%s.rgb" % self.label, "\n".join(lines) )

		yield (self.start, Instruction(".INCBIN \"%s\""% file_name, preamble=self.label+":"))

class GraphicDecoder(Decoder):
	def __init__(self, label, start, end, bit_depth=4, width=128, palette=None, palette_offset=0):
		Decoder.__init__(self, label, start, end)
		self.bit_depth = bit_depth
		self.width = width
		self.palette = palette
		self.palette_offset = palette_offset

		if self.palette != None:
			if (1 << self.bit_depth) > self.palette.colorCount() - self.palette_offset:
				raise ValueError("Palette %s does not provide enough colors for %d-bit graphic %s" % (self.palette.label, self.bit_depth, self.label))

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

	def get_palette(self):
		if self.palette != None:
			return self.palette.colors[self.palette_offset:]
		else:
			# Gray scale palette
			step = 1 << (8 - self.bit_depth) 
			return [ (x << 10 | x << 18 | x << 2) for x in xrange(0, 256, step) ]

	def decode(self, cart):
		# Output chr file
		file_name = "%s_%dbpp.chr" % (self.label, self.bit_depth)
		self.add_file(file_name, bytearray(cart[self.start:self.end]))

		# Output bitmap file
		tile_count = (self.end - self.start) / self.tile_size
		tiles_wide = self.width / 8
		height = (tile_count / tiles_wide) * 8
		if tile_count % tiles_wide != 0:
			height = height + 8

		# If palette hasn't been decoded yet then decode now
		if self.palette != None and len(self.palette.colors) == 0:
			next(self.palette.decode(cart))

		bitmap = BitmapIndex(self.width, height, self.bit_depth, self.get_palette())

		tile_index = 0
		for i in xrange(self.start, self.end, self.tile_size):
			tile = self.tile_decoder(cart[i:i+self.tile_size])

			tile_x = (tile_index % tiles_wide) * 8
			tile_y = (tile_index / tiles_wide) * 8
			for y in xrange(0,8):
				for x in xrange(0,8):
					bitmap.setPixel(tile_x+x,tile_y+y, tile[y*8+x])
			tile_index = tile_index + 1

		self.add_file("%s_%dbpp.bmp" % (self.label, self.bit_depth), bitmap.output())

		# Make binary chr file include
		yield (self.start, Instruction(".INCBIN \"%s\""% file_name, preamble=self.label+":"))


class TranlationMap(Decoder):
	def __init__(self, label, table):
		Decoder.__init__(self, label)
		self.table = { i: table[i] if i in table else chr(i) for i in xrange(0,256)}
		script = "\n".join(["%02x=%s" % (hex,ansi_escape(text)) for hex,text in self.table.items()])
		self.add_file("%s.tbl" % self.label, script.encode('utf-8'))

	def decode(self, cart):
		yield (self.start, Instruction('.STRINGMAPTABLE %s "%s.tbl"' % (self.label, self.label)))

class TileMapDecoder(Decoder):
	def __init__(self, label, start, end, bit_depth=4, width=128, palette=None, palette_offset=0):
		Decoder.__init__(self, label, start, end)


_ESCAPE_CHARS = {'\t': '\\t', '\n': '\\n', '\r': '\\r', '\x0b': '\\x0b', '\x0c': '\\x0c', '"': '\\"', '\x00': '\\' + '0'}

def ansi_escape(subject):
	return ''.join([_ESCAPE_CHARS[c] if c in _ESCAPE_CHARS else c for c in subject])

def quote_escape(subject):
	return subject.replace("\\", "\\\\")

