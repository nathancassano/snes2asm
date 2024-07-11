# -*- coding: utf-8 -*-

from snes2asm.compression.lz import lz_compress, lz_decompress

def compress(data):
	return lz1_compress(data).do()

def decompress(data):
	return lz1_decompress(data).do()

class lz1_compress(lz_compress):
	def __init__(self, data):
		lz_compress.__init__(self, data)
		self._functions = [self._rle16,self._rle8,self._increment_fill,self._repeat_le]

class lz1_decompress(lz_decompress):
	def __init__(self, data):
		lz_decompress.__init__(self, data)
		self._functions = [self._direct_copy, self._fill_byte, self._fill_word, self._inc_fill, self._repeat_le, self._noop, self._noop, self._long_command]

