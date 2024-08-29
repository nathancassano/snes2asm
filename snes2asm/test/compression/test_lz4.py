# -*- coding: utf-8 -*-

import unittest

from snes2asm.compression import lz4

class lz4_Test(unittest.TestCase):

    def test_compression(self):

        singleByte = bytearray([65])
        self.assertEqual(singleByte, lz4.decompress(lz4.compress(singleByte)))

        repeatByte = bytearray([64]*14)
        self.assertEqual(repeatByte, lz4.decompress(lz4.compress(repeatByte)))

        invertByte = bytearray([10,12,14,16,18,20,245,243,241,239,237,0,0])
        self.assertEqual(invertByte, lz4.decompress(lz4.compress(invertByte)))

        stringBytes = bytearray("aaaaaaaaaa12345cacacacaaaa6ca7c712a6b2248dc409d34b82e58876123a".encode('utf-8'))
        self.assertEqual(stringBytes, lz4.decompress(lz4.compress(stringBytes)))

if __name__ == '__main__':
    unittest.main()
