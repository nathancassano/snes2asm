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

if __name__ == '__main__':
    unittest.main()
