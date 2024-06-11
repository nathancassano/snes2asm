# -*- coding: utf-8 -*-

import unittest

from snes2asm.compression import rle1

class RLE1Test(unittest.TestCase):
	
	def test_compression(self):
	
		stringBytes = bytearray("aaaaaaaaaaaaaaca1aaaaa".encode('utf-8'))
		self.assertEqual(bytearray([0x80,13,97,0,2,99,97,49,0x80,4,97,0xFF,0xFF]), rle1.compress(stringBytes))
		self.assertEqual(stringBytes, rle1.decompress(rle1.compress(stringBytes)))

		stringBytes = bytearray("aaz".encode('utf-8'))
		self.assertEqual(bytearray([0x80,1,97,0,0,122,0xFF,0xFF]), rle1.compress(stringBytes))

		stringBytes = bytearray("azz".encode('utf-8'))
		self.assertEqual(bytearray([0,0,97,0x80,1,122,0xFF,0xFF]), rle1.compress(stringBytes))

		stringBytes = bytearray([0xFF] * (0xFF))
		self.assertEqual(bytearray([0x80,0x7f,0xFF,0x80,0x7E,0xFF,0xFF,0xFF]), rle1.compress(stringBytes))
		self.assertEqual(stringBytes, rle1.decompress(rle1.compress(stringBytes)))

if __name__ == '__main__':
    unittest.main()
