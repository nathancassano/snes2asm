# -*- coding: utf-8 -*-

import struct
from io import BytesIO

class BitmapIndex():
	def __init__(self, width, height, bits, palette):
		self._bfType = 19778 # Bitmap signature
		self._bfReserved1 = 0
		self._bfReserved2 = 0
		self._bfOffBits = 54 + len(palette)*4
		self._bcSize = 40
		self._bcWidth = width
		self._bcHeight = height
		self._bcPlanes = 1
		self._bcBitCount = bits
		self._bcTotalColors = len(palette)
		self._paddedWidth = self._bcWidth if (self._bcWidth * self._bcBitCount) / 8 & 0x3 == 0 else (self._bcWidth & ~0x3) + 4

		self._bfSize = 54 + self._graphicSize() + len(palette)*4

		if len(palette) > self._bcTotalColors:
			raise ValueError('Palette must be less than %d entries long' % self._bcTotalColors)

		if bits not in [1,2,4,8]:
			raise ValueError('Invalid index color bits')

		self._palette = palette
		self.clear()

	def _graphicSize(self):
		return max((self._bcBitCount*self._paddedWidth*self._bcHeight)/8, self._paddedWidth)

	def clear(self):
		self._graphics = bytearray(self._graphicSize())

	def setPixel(self, x, y, index):
		if x < 0 or y < 0 or x >= self._bcWidth or y >= self._bcHeight:
			raise ValueError('Coords (%d,%d) out of range' % (x,y))
		if index < 0 or index > self._bcTotalColors:
			raise ValueError('Color value %d must be inside index range of %d' % (index, self._bcTotalColors))

		stride = (self._bcHeight - 1 - y) * self._paddedWidth + x
		# 1-Bit
		if self._bcBitCount == 1:
			offset = stride / 8
			bitrow = stride & 0x7
			pixel = self._graphics[offset]
			pixel = pixel & ~(0x80 >> bitrow) | (index << 7) >> bitrow
			self._graphics[offset] = pixel & 0xFF
		# 2-Bit
		elif self._bcBitCount == 2:
			offset = stride / 4
			bitrow = (stride & 0x3) << 1
			pixel = self._graphics[offset]
			pixel = pixel & ~(0xC >> bitrow) | (index << 6) >> bitrow
			self._graphics[offset] = pixel & 0xFF
		# 4-Bit
		elif self._bcBitCount == 4:
			offset = stride / 2
			bitrow = (stride & 0x1) << 2
			pixel = self._graphics[offset]
			pixel = pixel & ~(0xF0 >> bitrow) | (index << 4) >> bitrow
			self._graphics[offset] = pixel & 0xFF
		# 8-Bit
		elif self._bcBitCount == 8:
			self._graphics[stride] = index

	def getPixel(self, x, y):
		if x < 0 or y < 0 or x >= self._bcWidth or y >= self._bcHeight:
			raise ValueError('Coords (%d,%d) out of range' % (x,y))
		stride = (self._bcHeight - 1 - y) * self._paddedWidth + x
		# 1-Bit
		if self._bcBitCount == 1:
			offset = stride / 8
			pixel = self._graphics[offset]
			return (pixel >> (~stride & 0x7)) & 0x1
		# 2-Bit
		elif self._bcBitCount == 2:
			offset = stride / 4
			pixel = self._graphics[offset]
			return (pixel >> ((~stride & 0x3) << 1)) & 0x3
		# 4-Bit
		elif self._bcBitCount == 4:
			offset = stride / 2
			pixel = self._graphics[offset]
			return (pixel >> ((~stride & 0x1) << 2)) & 0xF
		# 8-Bit
		elif self._bcBitCount == 8:
			return self._graphics[stride]

	def setGraphics(self, packedBytes):
		if type(packedBytes) != bytearray:
			raise ValueError('Packed bytes must be bytearray type')

		if len(packedBytes) != self._graphicSize():
			raise ValueError('Packed bytes must %d bytes in size instead of %d' % (self._graphicSize(), len(packedBytes)))

		self._graphics = packedBytes

	def output(self):
		io = BytesIO()

		# Writing BITMAPFILEHEADER
		io.write(struct.pack('<HLHHL', 
			self._bfType, 
			self._bfSize, 
			self._bfReserved1, 
			self._bfReserved2, 
			self._bfOffBits
			))

		# Writing BITMAPINFO
		io.write(struct.pack('<LLLHHLLLLLL', 
			self._bcSize, 
			self._bcWidth, 
			self._bcHeight, 
			self._bcPlanes, 
			self._bcBitCount,
			0, 0, 0, 0, 
			self._bcTotalColors, 
			0
			))
		for color in self._palette:
			io.write(struct.pack('<L', color))
		io.write(self._graphics)
		io.seek(0)
		return io.read()

	def write(self, file):
		with open(file, 'wb') as f:
			f.write(self.output())

	def __str__(self):
		return "Bitmap width=%d height=%d bits=%d colors=%d" % (self._bcWidth, self._bcHeight, self._bcBitCount, self._bcTotalColors)

	@staticmethod
	def read(file_name):
		with open(file_name, "rb") as f:
			file_data = f.read()

		header = struct.unpack('<HLHHLLLLHHLLLLLL', file_data[0:54])

		if header[0] != 19778:
			raise ValueError("The file %s is not a bitmap" % file_name)

		width = header[6]
		height = header[7]
		bits = header[9]
		compression = header[10]
		colors = header[14]

		if compression != 0:
			raise ValueError("Compressed bitmaps not supported of type 0x%02X" % compression)

		if bits not in [1,2,4,8]:
			raise ValueError("Not a 1-bit, 2-bit, 4-bit or 8-bit indexed bitmap")

		pal_offset = 14 + header[5]
		pal_size = colors * 4
		bit_offset = pal_offset + pal_size

		palette = []
		for i in xrange(pal_offset, bit_offset, 4):
			palette.append(struct.unpack('<L', file_data[i:i+4])[0])

		map = file_data[bit_offset:]

		bit = BitmapIndex(width, height, bits, palette)
		bit.setGraphics(bytearray(file_data[bit_offset:]))
		return bit
