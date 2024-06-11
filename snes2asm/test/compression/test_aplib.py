# -*- coding: utf-8 -*-

import unittest

from snes2asm.compression import aplib

class AplibTest(unittest.TestCase):
	
	def test_compression(self):
	
		singleByte = bytearray([53])
		self.assertEqual(singleByte, aplib.decompress(aplib.compress(singleByte)))
		stringBytes = bytearray("aaaaaaaaaaaaaacaaaaaa".encode('utf-8'))
		self.assertEqual(stringBytes, aplib.decompress(aplib.compress(stringBytes)))

if __name__ == '__main__':
    unittest.main()
