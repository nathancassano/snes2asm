# -*- coding: utf-8 -*-

import unittest

from snes2asm.compression import lz2

class lz2_Test(unittest.TestCase):
	
	def test_compression(self):
	
		singleByte = bytearray([65])
		self.assertEqual(singleByte, lz2.decompress(lz2.compress(singleByte)))

		repeatByte = bytearray([65]*14)
		self.assertEqual(repeatByte, lz2.decompress(lz2.compress(repeatByte)))

		stringBytes = bytearray("aaaaaaaaaaccaa".encode('utf-8'))
		self.assertEqual(stringBytes, lz2.decompress(lz2.compress(stringBytes)))

		stringBytes = bytearray("aaaaaaaaaa12345cacacacaaaa6ca7c712a6b2248dc409d34b82e58876123a".encode('utf-8'))
		self.assertEqual(stringBytes, lz2.decompress(lz2.compress(stringBytes)))


if __name__ == '__main__':
    unittest.main()
