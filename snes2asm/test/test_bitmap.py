# -*- coding: utf-8 -*-

import unittest
import os
from snes2asm.bitmap import *

class TileTest(unittest.TestCase):

	def test_readbmp(self):
		b = BitmapIndex.read(os.path.join(os.path.dirname(__file__), "test.bmp"))

		self.assertEqual(70, b._bfOffBits)
		self.assertEqual(4, b._bcWidth)
		self.assertEqual(4, b._bcHeight)
		self.assertEqual(4, b._bcBitCount)
		self.assertEqual(4, b._bcTotalColors)
		self.assertEqual(8, b._paddedWidth)

		self.assertEqual(0, b.getPixel(0,0))
		self.assertEqual(1, b.getPixel(3,3))

		b.setPixel(0,3,3)
		self.assertEqual(3, b.getPixel(0,3))

		b.setPixel(1,2,3)
		self.assertEqual(3, b.getPixel(1,2))

	def test_createbmp(self):
		b = BitmapIndex(8,8,4,[0xFF00, 0, 0, 0]*4)
		b.setPixel(0,0,1)
		b.output()

	def test_create4bmp(self):
		b = BitmapIndex(128,72,4,[0, 0xFF00, 0, 0]*4)
		for x in range(0,128):
			for y in range(0, 72):
				if x > 24 and y > 64:
					pass
				else:
					b.setPixel(x,y,1)

		b.write("output128x64.bmp")
		os.unlink("output128x64.bmp")


if __name__ == '__main__':
    unittest.main()
