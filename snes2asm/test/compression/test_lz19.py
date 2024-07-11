# -*- coding: utf-8 -*-

import unittest

from snes2asm.compression import lz19

class lz19_Test(unittest.TestCase):
	
	def test_compression(self):
	
		singleByte = bytearray([65])
		self.assertEqual(singleByte, lz19.decompress(lz19.compress(singleByte)))

		repeatByte = bytearray([65]*14)
		self.assertEqual(repeatByte, lz19.decompress(lz19.compress(repeatByte)))

		reverseBitByte = bytearray([0,0,0xF,0xF,0xF,0xF,20,0xF0,0xF0,0xF0,0xF0,45])
		self.assertEqual(reverseBitByte, lz19.decompress(lz19.compress(reverseBitByte)))

		stringBytes = bytearray("aaaaaaaaaaccaa".encode('utf-8'))
		self.assertEqual(stringBytes, lz19.decompress(lz19.compress(stringBytes)))

		stringBytes = bytearray("aaaaaaaaaa12345cacacacaaaa6ca7c712a6b2248dc409d34b82e58876123a".encode('utf-8'))
		self.assertEqual(stringBytes, lz19.decompress(lz19.compress(stringBytes)))

if __name__ == '__main__':
    unittest.main()
