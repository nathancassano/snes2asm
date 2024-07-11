# -*- coding: utf-8 -*-

from snes2asm.compression.lz import lz_compress, lz_decompress

def compress(data):
	return lz19_compress(data).do()

def decompress(data):
	return lz19_decompress(data).do()

class lz19_compress(lz_compress):

	REPEAT_BITREV = 5
	REPEAT_REV = 6

	def __init__(self, data):
		lz_compress.__init__(self, data)
		self._functions = [self._rle16,self._rle8,self._increment_fill,self._repeat_be,self._repeat_reverse,self._repeat_bit_reverse]

	def _repeat_bit_reverse(self):
		length, index = self._search_bit_reverse()
		return (self.REPEAT_BITREV, length, bytearray([index & 0xFF, index >> 8]))

	def _repeat_reverse(self):
		length, index = self._search_reverse()
		return (self.REPEAT_REV, length, bytearray([index & 0xFF, index >> 8]))

class lz19_decompress(lz_decompress):
	def __init__(self, data):
		lz_decompress.__init__(self, data)
		self._functions = [self._direct_copy, self._fill_byte, self._fill_word, self._inc_fill, self._repeat_be, self._repeat_bit_reverse, self._repeat_reverse, self._long_command]

