# -*- coding: utf-8 -*-

import unittest

from snes2asm.compression import rle2

class RLE2Test(unittest.TestCase):
	
	def test_compression(self):
	
		stringBytes = bytearray("aaaaaaaaaaaaaaca1aaaaa".encode('utf-8'))
		self.assertEqual(stringBytes, rle2.decompress(rle2.compress(stringBytes)))

		stringBytes = bytearray("azazaz12222234".encode('utf-8'))
		self.assertEqual(stringBytes, rle2.decompress(rle2.compress(stringBytes)))

if __name__ == '__main__':
    unittest.main()
