# -*- coding: utf-8 -*-

from snes2asm.compression.lz import lz_compress, lz_decompress, bit_reverse

def compress(data):
	return lz3_compress(data).do()

def decompress(data):
	return lz3_decompress(data).do()

class lz3_compress(lz_compress):

	REPEAT_BITREV = 5
	REPEAT_REV = 6

	def __init__(self, data):
		lz_compress.__init__(self, data)
		self._functions = [self._rle16,self._rle8,self._zero_fill,self._repeat_rel,self._repeat_reverse,self._repeat_bit_reverse]

	def _repeat_rel(self):
		return self._repeat_func(self.REPEAT, self._search)

	def _repeat_bit_reverse(self):
		return self._repeat_func(self.REPEAT_BITREV, self._search_bit_reverse)

	def _repeat_reverse(self):
		return self._repeat_func(self.REPEAT_REV, self._search_reverse)

	def _repeat_func(self, command, search_func):
		length, index = search_func()
		relative_index = self._offset - index
		if  relative_index < 128:
			return (command, length, bytearray([relative_index | 0x80]))
		else:
			return (command, length, bytearray([(index >> 8) & 0x7F, index & 0xFF]))

class lz3_decompress(lz_decompress):
	def __init__(self, data):
		lz_decompress.__init__(self, data)
		self._functions = [self._direct_copy, self._fill_byte, self._fill_word, self._fill_zero, self._repeat_rel, self._repeat_bit_reverse, self._repeat_reverse, self._long_command]

	def _repeat_data(self):
		index = self._in[self._offset]
		if index & 0x80 != 0:
			start = len(self._out) - (index & 0x7F)
			self._offset += 1
		else:
			start = index << 8 | self._in[self._offset+1]
			self._offset += 2
		end = start + self._length
		return self._out[start:end]

	def _repeat_rel(self):
		self._out += self._repeat_data()

	def _repeat_bit_reverse(self):
		self._out += bytearray([bit_reverse(b) for b in self._repeat_data()])

	def _repeat_reverse(self):
		self._out += self._repeat_data()[::-1]
