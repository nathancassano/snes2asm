# -*- coding: utf-8 -*-

import unittest
from snes2asm.bitmap import *

class TileTest(unittest.TestCase):

	def test_readbmp(self):
		b = BitmapIndex.read("snes2asm/tests/test.bmp")

		self.assertEquals(70, b._bfOffBits)
		self.assertEquals(4, b._bcWidth)
		self.assertEquals(4, b._bcHeight)
		self.assertEquals(4, b._bcBitCount)
		self.assertEquals(4, b._bcTotalColors)
		self.assertEquals(8, b._paddedWidth)

		self.assertEquals(0, b.getPixel(0,0))
		self.assertEquals(1, b.getPixel(3,3))

		b.setPixel(0,3,3)
		self.assertEquals(3, b.getPixel(0,3))

		b.setPixel(1,2,3)
		self.assertEquals(3, b.getPixel(1,2))

	def test_createbmp(self):
		b = BitmapIndex(8,8,4,[0xFF00, 0, 0, 0]*4)
		b.setPixel(0,0,1)
		b.output()

	def test_create4bmp(self):
		b = BitmapIndex(128,72,4,[0, 0xFF00, 0, 0]*4)
		for x in xrange(0,128):
			for y in xrange(0, 72):
				if x > 24 and y > 64:
					pass
				else:
					b.setPixel(x,y,1)

		b.write("output128x64.bmp")


if __name__ == '__main__':
    unittest.main()
