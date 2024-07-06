# -*- coding: utf-8 -*-

import unittest

from snes2asm.compression import lz1

class lz1_Test(unittest.TestCase):
	
	def test_compression(self):
	
		singleByte = bytearray([65])
		self.assertEqual(singleByte, lz1.decompress(lz1.compress(singleByte)))

		repeatByte = bytearray([65]*14)
		self.assertEqual(repeatByte, lz1.decompress(lz1.compress(repeatByte)))

		stringBytes = bytearray("aaaaaaaaaaccaa".encode('utf-8'))
		self.assertEqual(stringBytes, lz1.decompress(lz1.compress(stringBytes)))

		stringBytes = bytearray("aaaaaaaaaa12345cacacacaaaa6ca7c712a6b2248dc409d34b82e58876123a".encode('utf-8'))
		self.assertEqual(stringBytes, lz1.decompress(lz1.compress(stringBytes)))


if __name__ == '__main__':
    unittest.main()
