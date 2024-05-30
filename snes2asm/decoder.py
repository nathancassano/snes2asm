# -*- coding: utf-8 -*-

from snes2asm.disassembler import Instruction
from snes2asm.tile import Decode8bppTile, Decode4bppTile, Decode3bppTile, Decode2bppTile, DecodeMode7Tile
from snes2asm.bitmap import BitmapIndex
from snes2asm import compression

import struct
import yaml

class Decoder:
	def __init__(self, label=None, start=0, end=0, compress=None):
		self.label = label
		self.start = start
		self.end = end
		self.files = {}
		self.compress = compress
		self.sub_decoders = []

		if type(self.label) != str:
				raise TypeError("Invalid value for label parameter: %s" % str(self.label))
		if type(self.start) != int:
				raise TypeError("Invalid value for start parameter: %s" % str(self.start))
		if type(self.end) != int:
				raise TypeError("Invalid value for end parameter: %s" % str(self.end))

	def name(self):
		return "%s%06x-%06x" % (self.__name__, self.start, self.end)

	def decode(self, data):
		show_label = self.label != None
		for y in range(0, len(data), 16):
			line = '.db ' + ', '.join(("$%02X" % x) for x in data[y : min(y+16, len(data))])
			if show_label:
				yield (y, Instruction(line, preamble=self.label+":"))
				show_label = False
			else:
				yield (y, Instruction(line))

	def no_data(self):
		return self.start == self.end

	def add_file(self, name, data):
		if self.compress != None:
			compfile = "%s.%s" % (name, self.compress)
			self.files[compfile] = data
		self.files[name] = data

	@staticmethod
	def val(data, pos, size=1):
		if size == 2:
			return data[pos] + (data[pos+1] << 8)
		elif size == 3:
			return data[pos] + (data[pos+1] << 8) + (data[pos+2] << 16)
		elif size == 4:
			return data[pos] + (data[pos+1] << 8) + (data[pos+2] << 16) + (data[pos+3] << 24)
		else:
			return data[pos]

	@staticmethod
	def data_directive(size):
		return ['.db', '.dw', '.dl', '.dd'][(size-1) & 0x3]

	def decompress(self, data):
		try:
			module = getattrib(compression, self.compress)
		except AttributeError:
			raise ValueError("Decoder %s has an invalid compression type of %s" % (self.label, self.compress))
		return module.decompress(data) 


class Headers(Decoder):
	def __init__(self, start, end):
		Decoder.__init__(self, label="Headers", start=start, end=end)

	def decode(self, data):
		yield (0, Instruction('; Auto-generated headers', preamble=self.label+":"))

class BinaryDecoder(Decoder):
	def __init__(self, label, start, end, compress=None):
		Decoder.__init__(self, label, start, end, compress)

	def decode(self, data):
		self.add_file("%s.bin" % self.label, data)
		yield (0, Instruction(".INCBIN \"%s.bin\"" % self.label, preamble=self.label+":"))

class TextDecoder(Decoder):
	def __init__(self, label, start, end=0, compress=None, pack=None, index=None, translation=None):
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

		Decoder.__init__(self, label, start, end, compress)
		self.translation = translation
		self.pack = pack
		self.index = index
		if self.index != None:
			self.sub_decoders.append(index)

	def decode(self, data):
		if self.pack:
			pos = 0
			for index in range(0, len(self.pack)):
				size = self.pack[index]
				label = "%s_%d:" % (self.label, index)
				end = pos + size
				yield self.text(pos, data[pos:end], label)
				pos = end
		elif self.index:
			pos = 0
			index = 0
			for offset in self.index.values:
				yield self.text(pos, data[pos:offset], "%s_%d:" % (self.label, index))
				pos = offset
				index += 1

			if pos < self.end:
				yield self.text(pos, data[pos:self.end], "%s_%d:" % (self.label, index))

		else:
			yield self.text(0, data, self.label+":")

	def text(self, pos, input, label):
		if self.translation:
			# Break STRINGMAP directives into multiple parts if needed
			# since there is a bug with large buffers in WLA-DX
			parts = []
			for output_start in range(0, len(input), 256):
				out = []
				output_end = min(output_start+256,len(input))
				for char in input[output_start:output_end]:
					if char in self.translation.table:
						out.append(self.translation.table[char])
					else:
						out.append(_ESCAPE_CHARS[char])
				parts.append('.STRINGMAP %s "%s"' % (self.translation.label, "".join(out)))
			return (pos, Instruction("\n".join(parts), preamble=label))
		else:
			output = ansi_escape(input)
			return (pos, Instruction('.db "%s"' % output, preamble=label))

class ArrayDecoder(Decoder):

	hex_fmt = ['$%02X', '$%04X', '$%06X', '$%08X']

	def __init__(self, label, start, end, compress=None, size=1, struct=None):
		Decoder.__init__(self, label, start, end, compress)
		self.size = size
		self.struct = struct

		if self.struct == None and (self.size > 4 or self.size < 1):
			raise ValueError("ArrayDecoder: Invalid array element size %d for label %s" % (self.size, label))

		if (end - start) % size != 0:
			raise ValueError("ArrayDecoder: %s start and end do not align with size %i" % (label, size))

	def decode(self, data):
		if self.struct != None:
			# TODO
			pass
		else:
			instr = Decoder.data_directive(self.size) + ' '
			form = self.hex_fmt[self.size-1]
			show_label = self.label != None
			for y in range(0, len(data), 16):
				parts = [form % Decoder.val(data, x, self.size) for x in range(y, min(y+16,len(data)), self.size)]
				line = instr + ', '.join(parts)
				if show_label:
					yield (y, Instruction(line, preamble=self.label+":"))
					show_label = False
				else:
					yield (y, Instruction(line))

class IndexDecoder(Decoder):
	def __init__(self, label, start, end, compress=None, size=2):
		Decoder.__init__(self, label, start, end, compress)
		if (end - start) % size != 0:
			raise ValueError("Index: %s start and end do not align with size %i" % (label, size))
		self.size = size
		self.parent = None
		self.values = []

	def decode(self, data):
		instr = Decoder.data_directive(self.size)
		index = 0
		for pos in range(0, len(data), self.size):
			offset = Decoder.val(data, pos, self.size)
			self.values.append(offset)
			if offset + self.parent.start > self.parent.end:
				yield(pos, Instruction('%s %i' % (instr, offset), comment='Invalid index'))
			else:
				yield(pos, Instruction('%s %s_%i - %s_0' % (instr, self.parent.label, index, self.parent.label), 
					preamble="%s_%i:" % (self.label, index)))
			index = index + 1

	def size(self):
		return (self.end - self.start) // self.size

class PaletteDecoder(Decoder):
	def __init__(self, start, end, compress=None, label=None):
		Decoder.__init__(self, label, start, end, compress)
		self.colors = []
		if (self.end - self.start) & 0x1 != 0:
			raise ValueError("Palette %s start and end (0x%06X-0x%06X) do not align with 2-byte color entries" % (self.label, self.start, self.end))

	def colorCount(self):
		return (self.end - self.start) / 2

	def filename(self):
		return "%s.pal" % self.label

	def decode(self, data):
		# Output pal file
		self.add_file(self.filename(), data)

		lines = []
		for i in range(0, len(data), 2):
			bgr565 = data[i] | data[i+1] << 8
			rgbcolor = ((bgr565 & 0x7c00) >> 7 | (bgr565 & 0x3e0) << 6 | (bgr565 & 0x1f) << 19)
			self.colors.append(rgbcolor)
			lines.append("#%06X" % rgbcolor)

		self.add_file("%s.rgb" % self.label, "\n".join(lines) )

		yield (0, Instruction(".INCBIN \"%s\""% self.filename(), preamble=self.label+":"))

class GraphicDecoder(Decoder):
	def __init__(self, label, start, end, compress=None, bit_depth=4, width=128, palette=None, palette_offset=0, mode7=False):
		Decoder.__init__(self, label, start, end, compress)
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
			self.sub_decoders.append(self.palette)
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

	def decode(self, data):
		# Output chr file
		file_name = "%s_%dbpp.chr" % (self.label, self.bit_depth)
		self.add_file(file_name, data)

		# Output bitmap file
		tile_count = int((self.end - self.start) / self.tile_size)
		tiles_wide = int(self.width / 8.0)
		height = int((tile_count / tiles_wide) * 8)
		if tile_count % tiles_wide != 0:
			height = height + 8

		# TODO: RE
		# If palette hasn't been decoded yet then decode now
		if self.palette != None and len(self.palette.colors) == 0:
			next(self.palette.decode(data))

		# Convert 3bpp to 4bpp for bitmap storage
		bitmap_depth = 4 if self.bit_depth == 3 else self.bit_depth
		bitmap = BitmapIndex(self.width, height, bitmap_depth, self.get_palette())

		tile_index = 0
		for i in range(0, len(data), self.tile_size):
			tile = self.tile_decoder(data[i:i+self.tile_size])

			tile_x = (tile_index % tiles_wide) * 8
			tile_y = (tile_index // tiles_wide) * 8
			for y in range(0,8):
				for x in range(0,8):
					pix = tile[y*8+x]
					bitmap.setPixel(tile_x+x,tile_y+y, pix)
			tile_index = tile_index + 1

		self.add_file(self.filename(), bitmap.output())

		# Make binary chr file include
		yield (0, Instruction(".INCBIN \"%s\""% file_name, preamble=self.label+":"))

class TranslationMap(Decoder):
	def __init__(self, label, table):
		Decoder.__init__(self, label)
		self.table = table
		# Fill is escape characters
		for i, k in {0: '\\0', 10: '[n]', 13: '[r]'}.items():
			if i not in self.table:
				self.table[i] = k

		self.table = { i: table[i] if i in table else chr(i) for i in range(0,256)}
		script = "\r\n".join(["%02x=%s" % (hex,text) for hex,text in self.table.items()])
		self.add_file("%s.tbl" % self.label, script.encode('utf-8'))

	def decode(self, data):
		yield (0, Instruction('.STRINGMAPTABLE %s "%s.tbl"' % (self.label, self.label)))

class TileMapDecoder(Decoder):
	def __init__(self, label, start, end, gfx, compress = None, width=128, encoding=None):
		Decoder.__init__(self, label, start, end, compress)
		self.gfx = gfx
		self.width = width
		self.height = int((self.end - self.start) / (width * 2))
		self.encoding = encoding

		if self.encoding != None and self.encoding not in ['rle', 'lzss']:
			raise ValueError("Unsupported encoding %s" % self.encoding)

	def decode(self, data):
		# Tilemap file
		tilebin = "%s.tilebin" % self.label
		if type(self.gfx) == list:
			gfx = [ g.filename() for g in self.gfx ]
			palette = [ g.palette.filename() for g in self.gfx ]
		else:
			gfx = self.gfx.filename()
			palette = self.gfx.palette.filename()

		tilemap = {'name': self.label, 'width': self.width, 'height': self.height, 'tilebin': tilebin, 'gfx': gfx, 'palette': palette}
		if self.encoding != None:
			tilemap['encoding'] = self.encoding
		self.add_file("%s.tilemap" % self.label, yaml.dump(tilemap).encode('utf-8'))

		# Tile character map file
		self.add_file(tilebin, data)
		yield (0, Instruction(".INCBIN \"%s.tilebin\"" % self.label, preamble=self.label+":"))

_ESCAPE_CHARS = ['\\' + '0', '\\x01', '\\x02', '\\x03', '\\x04', '\\x05', '\\x06', '\\x07', '\\x08', '\\t', '\\n', '\\x0b', '\\x0c', '\\r', '\\x0e', '\\x0f', '\\x10', '\\x11', '\\x12', '\\x13', '\\x14', '\\x15', '\\x16', '\\x17', '\\x18', '\\x19', '\\x1a', '\\x1b', '\\x1c', '\\x1d', '\\x1e', '\\x1f', ' ', '!', '\\"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?', '@', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '[', '\\', ']', '^', '_', '`', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~', '\x7f', '\\x80', '\\x81', '\\x82', '\\x83', '\\x84', '\\x85', '\\x86', '\\x87', '\\x88', '\\x89', '\\x8a', '\\x8b', '\\x8c', '\\x8d', '\\x8e', '\\x8f', '\\x90', '\\x91', '\\x92', '\\x93', '\\x94', '\\x95', '\\x96', '\\x97', '\\x98', '\\x99', '\\x9a', '\\x9b', '\\x9c', '\\x9d', '\\x9e', '\\x9f', '\\xa0', '\\xa1', '\\xa2', '\\xa3', '\\xa4', '\\xa5', '\\xa6', '\\xa7', '\\xa8', '\\xa9', '\\xaa', '\\xab', '\\xac', '\\xad', '\\xae', '\\xaf', '\\xb0', '\\xb1', '\\xb2', '\\xb3', '\\xb4', '\\xb5', '\\xb6', '\\xb7', '\\xb8', '\\xb9', '\\xba', '\\xbb', '\\xbc', '\\xbd', '\\xbe', '\\xbf', '\\xc0', '\\xc1', '\\xc2', '\\xc3', '\\xc4', '\\xc5', '\\xc6', '\\xc7', '\\xc8', '\\xc9', '\\xca', '\\xcb', '\\xcc', '\\xcd', '\\xce', '\\xcf', '\\xd0', '\\xd1', '\\xd2', '\\xd3', '\\xd4', '\\xd5', '\\xd6', '\\xd7', '\\xd8', '\\xd9', '\\xda', '\\xdb', '\\xdc', '\\xdd', '\\xde', '\\xdf', '\\xe0', '\\xe1', '\\xe2', '\\xe3', '\\xe4', '\\xe5', '\\xe6', '\\xe7', '\\xe8', '\\xe9', '\\xea', '\\xeb', '\\xec', '\\xed', '\\xee', '\\xef', '\\xf0', '\\xf1', '\\xf2', '\\xf3', '\\xf4', '\\xf5', '\\xf6', '\\xf7', '\\xf8', '\\xf9', '\\xfa', '\\xfb', '\\xfc', '\\xfd', '\\xfe', '\\xff']


def ansi_escape(subject):
	if type(subject) == str:
		return ''.join([_ESCAPE_CHARS[ord(c)] for c in subject])
	else:
		return ''.join([_ESCAPE_CHARS[c] for c in subject])
