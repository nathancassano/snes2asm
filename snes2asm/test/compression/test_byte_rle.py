# -*- coding: utf-8 -*-

import unittest

from snes2asm.compression import byte_rle

class byte_rle_Test(unittest.TestCase):
	
	def test_compression(self):
	
		singleByte = bytearray([53])
		self.assertEqual(singleByte, byte_rle.decompress(byte_rle.compress(singleByte)))
		stringBytes = bytearray("aaaaaaaaaaccaacccaaaa6ca7c712a6b2248dc409d34b82e58876".encode('utf-8'))
		self.assertEqual(stringBytes, byte_rle.decompress(byte_rle.compress(stringBytes)))

if __name__ == '__main__':
    unittest.main()
