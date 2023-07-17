# -*- coding: utf-8 -*-

from snes2asm.disassembler import Instruction
from snes2asm.tile import Decode8bppTile, Decode4bppTile, Decode3bppTile, Decode2bppTile, DecodeMode7Tile
from snes2asm.bitmap import BitmapIndex
import struct
import yaml

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

	def val(cart, pos, size=1):
		if size == 2:
			return cart[pos] + (cart[pos+1] << 8)
		elif size == 3:
			return cart[pos] + (cart[pos+1] << 8) + (cart[pos+2] << 16)
		elif size == 4:
			return cart[pos] + (cart[pos+1] << 8) + (cart[pos+2] << 16) + (cart[pos+3] << 24)
		else:
			return cart[pos]

	def data_directive(size):
		return ['.db', '.dw', '.dl', '.dd'][(size-1) & 0x3]


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
	def __init__(self, label, start, end=0, pack=None, index=None, translation=None):
		if pack != None:
			if type(pack) is not list:
				raise ValueError("TextDecoder: %s pack parameter must be an array" % label)
			# Calculate end from pack
			packsize = sum(pack)
			if end == 0:
				end = start + packsize
			elif start + packsize != end:
				raise ValueError("TextDecoder: %s pack lengths do not match end point" % label)
		elif index != None:
			index.parent = self
			if end == 0:
				raise ValueError("TextDecoder: %s missing end parameter" % label)

		Decoder.__init__(self, label, start, end)
		self.translation = translation
		self.pack = pack
		self.index = index

	def decode(self, cart):
		if self.pack:
			pos = self.start
			for index in range(0, len(self.pack)):
				size = self.pack[index]
				label = "%s_%d:" % (self.label, index)
				end = pos + size
				yield self.text(pos, cart[pos:end], label)
				pos = end
		elif self.index:
			pos = self.start
			index = 0
			for index_pos in range(self.index.start, self.index.end, self.index.size):
				if index_pos == self.index.start:
					continue
				offset = self.start + Decoder.val(cart, index_pos)
				if offset >=  self.end:
					print("TextDecoder: %s skipping out of range index %d" % (self.label, index))
					continue
				yield self.text(pos, cart[pos:offset], "%s_%d:" % (self.label, index))
				pos = offset
				index = index + 1

			if pos < self.end:
				yield self.text(pos, cart[pos:self.end], "%s_%d:" % (self.label, index))

		else:
			yield self.text(self.start, cart[self.start:self.end], self.label+":")

	def text(self, pos, input, label):
		if self.translation:
			out = []
			for char in input:
				if char in self.translation.table:
					out.append(self.translation.table[char])
				else:
					out.append(chr(char))
			output = ansi_escape("".join(out))
			return (pos, Instruction('.STRINGMAP %s "%s"' % (self.translation.label, quote_escape(output)), preamble=label))
		else:
			output = ansi_escape(str(input.decode()))
			return (pos, Instruction('.db "%s"' % quote_escape(output), preamble=label))

class ArrayDecoder(Decoder):

	hex_fmt = ['$%02X', '$%04X', '$%06X', '$%08X']

	def __init__(self, label, start, end, size=1, struct=None):
		Decoder.__init__(self, label, start, end)
		self.size = size
		self.struct = struct

		if self.struct == None and (self.size > 4 or self.size < 1):
			raise ValueError("ArrayDecoder: Invalid array element size %d for label %s" % (self.size, label))

		if (end - start) % size != 0:
			raise ValueError("ArrayDecoder: %s start and end do not align with size %i" % (label, size))

	def decode(self, cart):
		if self.struct != None:
			# TODO
			pass
		else:
			instr = Decoder.data_directive(self.size) + ' '
			form = self.hex_fmt[self.size-1]
			show_label = self.label != None
			for y in range(self.start, self.end, 16):
				parts = [form % Decoder.val(cart, x, self.size) for x in range(y, min(y+16,self.end), self.size)]
				line = instr + ', '.join(parts)
				if show_label:
					yield (y, Instruction(line, preamble=self.label+":"))
					show_label = False
				else:
					yield (y, Instruction(line))

class IndexDecoder(Decoder):
	def __init__(self, label, start, end, size=2):
		Decoder.__init__(self, label, start, end)
		if (end - start) % size != 0:
			raise ValueError("Index: %s start and end do not align with size %i" % (label, size))
		self.size = size
		self.parent = None

	def decode(self, cart):
		instr = Decoder.data_directive(self.size)
		index = 0
		for pos in range(self.start, self.end, self.size):
			offset = Decoder.val(cart, pos, self.size)
			if offset + self.parent.start > self.parent.end:
				yield(pos, Instruction('%s %i' % (instr, offset), comment='Invalid index'))
			else:
				yield(pos, Instruction('%s %s_%i - %s_0' % (instr, self.parent.label, index, self.parent.label)))
			index = index + 1
			pre = None

class PaletteDecoder(Decoder):
	def __init__(self, start, end, label=None):
		Decoder.__init__(self, label, start, end)
		self.colors = []
		if (self.end - self.start) & 0x1 != 0:
			raise ValueError("Palette %s start and end (0x%06X-0x%06X) do not align with 2-byte color entries" % (self.label, self.start, self.end))

	def colorCount(self):
		return (self.end - self.start) / 2

	def filename(self):
		return "%s.pal" % self.label

	def decode(self, cart):
		# Output pal file
		self.add_file(self.filename(), bytearray(cart[self.start:self.end]))

		lines = []
		for i in range(self.start, self.end, 2):
			bgr565 = cart[i] | cart[i+1] << 8
			rgbcolor = ((bgr565 & 0x7c00) >> 7 | (bgr565 & 0x3e0) << 6 | (bgr565 & 0x1f) << 19)
			self.colors.append(rgbcolor)
			lines.append("#%06X" % rgbcolor)

		self.add_file("%s.rgb" % self.label, "\n".join(lines) )

		yield (self.start, Instruction(".INCBIN \"%s\""% self.filename(), preamble=self.label+":"))

class GraphicDecoder(Decoder):
	def __init__(self, label, start, end, bit_depth=4, width=128, palette=None, palette_offset=0, mode7=False):
		Decoder.__init__(self, label, start, end)
		self.bit_depth = bit_depth
		self.width = width
		self.palette = palette
		self.palette_offset = palette_offset

		if self.width & 0x7 != 0:
			raise ValueError("Tile value width must be a multiple of 8")

		if mode7:
			self.bit_depth = 8
			self.tile_decoder = DecodeMode7Tile
			if self.palette_offset != 0:
				raise ValueError("Tile %s not allowed palette_offset for mode 7" % (self.label))
		elif self.bit_depth == 8:
			self.tile_decoder = Decode8bppTile
			self.tile_size = 64
		elif self.bit_depth == 2:
			self.tile_decoder = Decode2bppTile
			self.tile_size = 16
		elif self.bit_depth == 3:
			self.tile_decoder = Decode3bppTile
			self.tile_size = 24
		else:
			self.tile_decoder = Decode4bppTile
			self.tile_size = 32

		if self.palette != None:
			if (1 << self.bit_depth) > self.palette.colorCount() - self.palette_offset:
				raise ValueError("Palette %s does not provide enough colors for %d-bit graphic %s" % (self.palette.label, self.bit_depth, self.label))

		if (self.end - self.start) % self.tile_size != 0:
			raise ValueError("Tile %s start and end (0x%06X-0x%06X) do not align with the %d-bit tile size" % (self.label, self.start, self.end, self.bit_depth))

	def get_palette(self):
		if self.palette != None:
			return self.palette.colors[self.palette_offset:]
		else:
			# Gray scale palette
			step = 1 << (8 - self.bit_depth) 
			pal = [ ((x + step - 1) << 8 | (x + step - 1) << 16 | (x + step - 1) << 0) for x in range(0, 256, step) ]
			pal[0] = 0xFF00FF # Transparent
			pal[1] = 0        # True black
			return pal

	def filename(self):
		return "%s_%dbpp.bmp" % (self.label, self.bit_depth)

	def decode(self, cart):
		# Output chr file
		file_name = "%s_%dbpp.chr" % (self.label, self.bit_depth)
		self.add_file(file_name, bytearray(cart[self.start:self.end]))

		# Output bitmap file
		tile_count = int((self.end - self.start) / self.tile_size)
		tiles_wide = int(self.width / 8.0)
		height = int((tile_count / tiles_wide) * 8)
		if tile_count % tiles_wide != 0:
			height = height + 8

		# If palette hasn't been decoded yet then decode now
		if self.palette != None and len(self.palette.colors) == 0:
			next(self.palette.decode(cart))

		# Convert 3bpp to 4bpp for bitmap storage
		bitmap_depth = 4 if self.bit_depth == 3 else self.bit_depth
		bitmap = BitmapIndex(self.width, height, bitmap_depth, self.get_palette())

		tile_index = 0
		for i in range(self.start, self.end, self.tile_size):
			tile = self.tile_decoder(cart[i:i+self.tile_size])

			tile_x = (tile_index % tiles_wide) * 8
			tile_y = int(tile_index / tiles_wide) * 8
			for y in range(0,8):
				for x in range(0,8):
					pix = tile[y*8+x]
					bitmap.setPixel(tile_x+x,tile_y+y, pix)
			tile_index = tile_index + 1

		self.add_file(self.filename(), bitmap.output())

		# Make binary chr file include
		yield (self.start, Instruction(".INCBIN \"%s\""% file_name, preamble=self.label+":"))

class TranlationMap(Decoder):
	def __init__(self, label, table):
		Decoder.__init__(self, label)
		self.table = { i: table[i] if i in table else chr(i) for i in range(0,256)}
		script = "\n".join(["%02x=%s" % (hex,ansi_escape(text)) for hex,text in self.table.items()])
		self.add_file("%s.tbl" % self.label, script.encode('utf-8'))

	def decode(self, cart):
		yield (self.start, Instruction('.STRINGMAPTABLE %s "%s.tbl"' % (self.label, self.label)))

class TileMapDecoder(Decoder):
	def __init__(self, label, start, end, gfx, width=128, encoding=None):
		Decoder.__init__(self, label, start, end)
		self.gfx = gfx
		self.width = width
		self.height = int((self.end - self.start) / (width * 2))

	def decode(self, cart):
		# Tilemap file
		tilechr = "%s.tilechr" % self.label
		if type(self.gfx) == list:
			gfx = [ g.filename() for g in self.gfx ]
			palette = [ g.palette.filename() for g in self.gfx ]
		else:
			gfx = self.gfx.filename()
			palette = self.gfx.palette.filename()

		tilemap = {'name': self.label, 'width': self.width, 'height': self.height, 'tilechr': tilechr, 'gfx': gfx, 'palette': palette}
		self.add_file("%s.tilemap" % self.label, yaml.dump(tilemap).encode('utf-8'))

		# Tile character map file
		self.add_file(tilechr, bytearray(cart[self.start:self.end]))
		yield (self.start, Instruction(".INCBIN \"%s.tilechr\"" % self.label, preamble=self.label+":"))


_ESCAPE_CHARS = {'\t': '\\t', '\n': '\\n', '\r': '\\r', '\x0b': '\\x0b', '\x0c': '\\x0c', '"': '\\"', '\x00': '\\' + '0'}

def ansi_escape(subject):
	return ''.join([_ESCAPE_CHARS[c] if c in _ESCAPE_CHARS else c for c in subject])

def quote_escape(subject):
	return subject.replace("\\", "\\\\")

