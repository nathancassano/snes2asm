from functools import reduce
from snes2asm.compression.lz import lz_compress, lz_decompress

def compress(data):
	return lz2_compress(data).do()

def decompress(data):
	return lz2_decompress(data).do()

class lz2_compress(lz_compress):
	def __init__(self, data):
		lz_compress.__init__(self, data)
		self._functions = [self._rle16,self._rle8,self._increment_fill,self._repeat_be]

class lz2_decompress(lz_decompress):
	def __init__(self, data):
		lz_decompress.__init__(self, data)
		self._functions = [self._direct_copy, self._fill_byte, self._fill_word, self._inc_fill, self._repeat_be, self._noop, self._noop, self._long_command]

