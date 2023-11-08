# -*- coding: utf-8 -*-

def compress(data):
	return aplib_compress(data).do()

def decompress(data):
	return aplib_decompress(data).do()

class aplib_compress:
	"""
	aplib compression is based on lz77
	"""
	def __init__(self, data):
		self._in = data
		self._tagsize = 1
		self._tag = 0
		self._tagoffset = -1
		self._maxbit = (self._tagsize * 8) - 1
		self._curbit = 0
		self._isfirsttag = True
		self._offset = 0
		self._lastoffset = 0
		self._pair = True
		self.out = bytearray()

	def getdata(self):
		"""builds an output array of what's currently compressed:
		currently output bit + current tag content"""
		tagstr = int2lebin(self._tag, self._tagsize)
		return modifybytearray(self.out, tagstr, self._tagoffset)

	def write_bit(self, value):
		"""writes a bit, make space for the tag if necessary"""
		if self._curbit != 0:
			self._curbit -= 1
		else:
			if self._isfirsttag:
				self._isfirsttag = False
			else:
				self.out = self.getdata()
			self._tagoffset = len(self.out)
			self.out += bytearray([0] * self._tagsize)
			self._curbit = self._maxbit
			self._tag = 0

		if value:
			self._tag |= (1 << self._curbit)

	def write_bitstring(self, s):
		"""write a string of bits"""
		for c in s:
			self.write_bit(0 if c == "0" else 1)

	def write_byte(self, b):
		self.out.append(b)

	def write_fixednumber(self, value, nbbit):
		"""write a value on a fixed range of bits"""
		for i in range(nbbit - 1, -1, -1):
			self.write_bit( (value >> i) & 1)

	def write_variablenumber(self, value):
		length = getbinlen(value) - 2 # the highest bit is 1
		self.write_bit(value & (1 << length))
		for i in range(length - 1, -1, -1):
			self.write_bit(1)
			self.write_bit(value & (1 << i))
		self.write_bit(0)

	def _literal(self, marker=True):
		if marker:
			self.write_bit(0)
		self.write_byte(self._in[self._offset])
		self._offset += 1
		self._pair = True

	def _block(self, offset, length):
		self.write_bitstring("10")

		# if the last operations were literal or single byte
		# and the offset is unchanged since the last block copy
		# we can just store a 'null' offset and the length
		if self._pair and self._lastoffset == offset:
			self.write_variablenumber(2)
			self.write_variablenumber(length)
		else:
			high = (offset >> 8) + 2
			if self._pair:
				high += 1
			self.write_variablenumber(high)
			low = offset & 0xFF
			self.write_byte(low)
			self.write_variablenumber(length - lengthdelta(offset))
		self._offset += length
		self._lastoffset = offset
		self._pair = False

	def _shortblock(self, offset, length):
		self.write_bitstring("110")
		b = (offset << 1 ) + (length - 2)
		self.write_byte(b)
		self._offset += length
		self._lastoffset = offset
		self._pair = False

	def _singlebyte(self, offset):
		self.write_bitstring("111")
		self.write_fixednumber(offset, 4)
		self._offset += 1
		self._pair = True

	def _end(self):
		self.write_bitstring("110")
		self.write_byte(0)

	def do(self):
		self._literal(False)
		while self._offset < len(self._in):
			offset, length = find_longest_match(self._in[:self._offset], self._in[self._offset:])
			if length == 0:
				c = self._in[self._offset]
				if c == 0:
					self._singlebyte(0)
				else:
					self._literal()
			elif length == 1 and 0 <= offset < 16:
				self._singlebyte(offset)
			elif 2 <= length <= 3 and 0 < offset <= 127:
				self._shortblock(offset, length)
			elif 3 <= length and 2 <= offset:
				self._block(offset, length)
			else:
				self._literal()
		self._end()
		return self.getdata()

class aplib_decompress:
	def __init__(self, data):
		self._curbit = 0
		self._offset = 0
		self._tag = None
		self._tagsize = 1
		self._in = data
		self.out = bytearray()

		self._pair = True	# paired sequence
		self._lastoffset = 0
		self._functions = [self._literal, self._block, self._shortblock, self._singlebyte]

	def read_bit(self):
		"""read next bit from the stream, reloads the tag if necessary"""
		if self._curbit != 0:
			self._curbit -= 1
		else:
			self._curbit = (self._tagsize * 8) - 1
			self._tag = self.read_byte()
			for i in range(self._tagsize - 1):
				self._tag += self.read_byte() << (8 * (i + 1))

		bit = (self._tag >> ((self._tagsize * 8) - 1)) & 0x01
		self._tag <<= 1
		return bit

	def is_end(self):
		return self._offset == len(self._in) and self._curbit == 1

	def read_byte(self):
		"""read next byte from the stream"""
		result = self._in[self._offset]
		self._offset += 1
		return result

	def read_fixednumber(self, nbbit, init=0):
		"""reads a fixed bit-length number"""
		result = init
		for i in range(nbbit):
			result = (result << 1)  + self.read_bit()
		return result

	def read_variablenumber(self):
		"""return a variable bit-length number x, x >= 2

		reads a bit until the next bit in the pair is not set"""
		result = 1
		result = (result << 1) + self.read_bit()
		while self.read_bit():
			result = (result << 1) + self.read_bit()
		return result

	def read_setbits(self):
		"""read bits as long as their set or a maximum is reached"""
		result = 0
		while result < 3 and self.read_bit() == 1:
			result += 1
		return result

	def back_copy(self, offset, length=1):
		for i in range(length):
			self.out.append(self.out[-offset])

	def read_literal(self, value=None):
		if value is None:
			self.out.append(self.read_byte())
		else:
			self.out.append(value)

	def _literal(self):
		self.read_literal()
		self._pair = True
		return False

	def _block(self):
		b = self.read_variablenumber()	# 2-
		if b == 2 and self._pair :	# reuse the same offset
			offset = self._lastoffset
			length = self.read_variablenumber()	# 2-
		else:
			high = b - 2	# 0-
			if self._pair:
				high -= 1
			offset = (high << 8) + self.read_byte()
			length = self.read_variablenumber()	# 2-
			length += lengthdelta(offset)
		self._lastoffset = offset
		self.back_copy(offset, length)
		self._pair = False
		return False

	def _shortblock(self):
		b = self.read_byte()
		if b <= 1:	# likely 0
			return True
		length = 2 + (b & 0x01)	# 2-3
		offset = b >> 1	# 1-127
		self.back_copy(offset, length)
		self._lastoffset = offset
		self._pair = False
		return False

	def _singlebyte(self):
		offset = self.read_fixednumber(4) # 0-15
		if offset:
			self.back_copy(offset)
		else:
			self.read_literal(0)
		self._pair = True

	def do(self):
		"""returns decompressed buffer and consumed bytes counter"""
		self.read_literal()
		while True:
			if self._functions[self.read_setbits()]():
				break
		return self.out

def find_longest_match(s, sub):
	"""returns the number of byte to look backward and the length of byte to copy)"""
	if len(sub) == 0:
		return 0, 0
	limit = len(s)
	dic = bytearray(s)
	l = 0
	offset = 0
	length = 0
	first = 0
	word = bytearray() 
	word.append(sub[l])
	pos = dic.rfind(word, 0, limit + 1)
	if pos == -1:
		return offset, length

	offset = limit - pos
	length = len(word)
	dic.append(sub[l])

	while l < len(sub) - 1:
		l += 1
		word.append(sub[l])

		pos = dic.rfind(word, 0, limit + 1)
		if pos == -1:
			return offset, length
		offset = limit - pos
		length = len(word)
		dic.append(sub[l])
	return offset, length

def int2lebin(value, size):
	"""ouputs value in binary, as little-endian"""
	result = bytearray()
	for i in range(size):
		result.append((value >> (8 * i)) & 0xFF)
	return result

def modifybytearray(s, sub, offset):
	"""overwrites 'sub' at 'offset' of 's'"""
	return s[:offset] + sub + s[offset + len(sub):]

def getbinlen(value):
	"""return the bit length of an integer"""
	result = 0
	if value == 0:
		return 1
	while value != 0:
		value >>= 1
		result += 1
	return result

def lengthdelta(offset):
	l = 0
	if offset >= 32000:
		l += 1
	if offset >= 1280:
		l += 1
	if offset < 128:
		l += 2
	return l
