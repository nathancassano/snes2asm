from struct import pack

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
		self._bcTotalColors = 1 << bits

		self._bfSize = 54 + self._graphicSize() + len(palette)*4

		if len(palette) != self._bcTotalColors:
			raise ValueError('Palette must be %d entries long' % self._bcTotalColors)

		if bits not in [1,2,4,8]:
			raise ValueError('Invalid index color bits')

		self._palette = palette
		self.clear()

	def _graphicSize(self):
		return self._bcBitCount*self._bcWidth*self._bcHeight/8

	def clear(self):
		self._graphics = bytearray(self._graphicSize())

	def setPixel(self, x, y, index):
		if x < 0 or y < 0 or x >= self._bcWidth or y >= self._bcHeight:
			raise ValueError('Coords out of range')
		if index < 0 or index > self._bcTotalColors:
			raise ValueError('Color must be inside index range')

		stride = (self._bcHeight - 1 - y) * self._bcWidth + x
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
			self._graphics[offset] = pixel
		# 4-Bit
		elif self._bcBitCount == 4:
			offset = stride / 2
			bitrow = (stride & 0x1) << 2
			pixel = self._graphics[offset]
			pixel = pixel & ~(0xF0 >> bitrow) | (index << 4) >> bitrow
			self._graphics[offset] = pixel
		# 8-Bit
		elif self._bcBitCount == 8:
			self._graphics[stride] = index

	def setGraphics(self, packedBytes):
		if type(packedBytes) != bytearray:
			raise ValueError('Packed bytes must be bytearray type')

		if len(packedBytes) != self._graphicSize():
			raise ValueError('Packed bytes must %d bytes in size' % self._graphicSize())

		self._graphics = packedBytes

	def write(self, file):
		with open(file, 'wb') as f:
			# Writing BITMAPFILEHEADER
			f.write(pack('<HLHHL', 
				self._bfType, 
				self._bfSize, 
				self._bfReserved1, 
				self._bfReserved2, 
				self._bfOffBits
				))

			# Writing BITMAPINFO
			f.write(pack('<LLLHHLLLLLL', 
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
				f.write(pack('<L', color))
			f.write(self._graphics)
