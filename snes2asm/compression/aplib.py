
from io import BytesIO

def compress(data):
	return aplib_compress(data).do()

def decompress(data):
	return aplib_decompress(data).do()

class aplib_compress:
	"""
	aplib compression is based on lz77
	"""
	def __init__(self, data, length=None):
		self.out = bytearray()
		self.__tagsize = 1
		self.__tag = 0
		self.__tagoffset = -1
		self.__maxbit = (self.__tagsize * 8) - 1
		self.__curbit = 0
		self.__isfirsttag = True
		self.__in = BytesIO(data)
		self.__length = length if length is not None else len(data)
		self.__offset = 0
		self.__lastoffset = 0
		self.__pair = True

	def getdata(self):
		"""builds an output string of what's currently compressed:
		currently output bit + current tag content"""
		tagstr = int2lebin(self.__tag, self.__tagsize)
		return modifybytearray(self.out, tagstr, self.__tagoffset)

	def write_bit(self, value):
		"""writes a bit, make space for the tag if necessary"""
		if self.__curbit != 0:
			self.__curbit -= 1
		else:
			if self.__isfirsttag:
				self.__isfirsttag = False
			else:
				self.out = self.getdata()
			self.__tagoffset = len(self.out)
			self.out += bytearray([0] * self.__tagsize)
			self.__curbit = self.__maxbit
			self.__tag = 0

		if value:
			self.__tag |= (1 << self.__curbit)

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

	def __literal(self, marker=True):
		if marker:
			self.write_bit(0)
		self.write_byte(self.__in.getvalue()[self.__offset])
		self.__offset += 1
		self.__pair = True

	def __block(self, offset, length):
		self.write_bitstring("10")

		# if the last operations were literal or single byte
		# and the offset is unchanged since the last block copy
		# we can just store a 'null' offset and the length
		if self.__pair and self.__lastoffset == offset:
			self.write_variablenumber(2)	# 2-
			self.write_variablenumber(length)
		else:
			high = (offset >> 8) + 2
			if self.__pair:
				high += 1
			self.write_variablenumber(high)
			low = offset & 0xFF
			self.write_byte(low)
			self.write_variablenumber(length - lengthdelta(offset))
		self.__offset += length
		self.__lastoffset = offset
		self.__pair = False

	def __shortblock(self, offset, length):
		self.write_bitstring("110")
		b = (offset << 1 ) + (length - 2)
		self.write_byte(b)
		self.__offset += length
		self.__lastoffset = offset
		self.__pair = False

	def __singlebyte(self, offset):
		self.write_bitstring("111")
		self.write_fixednumber(offset, 4)
		self.__offset += 1
		self.__pair = True

	def __end(self):
		self.write_bitstring("110")
		self.write_byte(0)

	def do(self):
		self.__literal(False)
		while self.__offset < self.__length:
			offset, length = find_longest_match(self.__in.getvalue()[:self.__offset],
				self.__in.getvalue()[self.__offset:])
			if length == 0:
				c = self.__in.getvalue()[self.__offset]
				if c == 0:
					self.__singlebyte(0)
				else:
					self.__literal()
			elif length == 1 and 0 <= offset < 16:
				self.__singlebyte(offset)
			elif 2 <= length <= 3 and 0 < offset <= 127:
				self.__shortblock(offset, length)
			elif 3 <= length and 2 <= offset:
				self.__block(offset, length)
			else:
				self.__literal()
		self.__end()
		return self.getdata()

class aplib_decompress:
	def __init__(self, data):
		self.__curbit = 0
		self.__offset = 0
		self.__tag = None
		self.__tagsize = 1
		self.__in = BytesIO(data)
		self.out = bytearray()

		self.__pair = True	# paired sequence
		self.__lastoffset = 0
		self.__functions = [
			self.__literal,
			self.__block,
			self.__shortblock,
			self.__singlebyte]

	def getoffset(self):
		"""return the current byte offset"""
		return self.__offset

	def read_bit(self):
		"""read next bit from the stream, reloads the tag if necessary"""
		if self.__curbit != 0:
			self.__curbit -= 1
		else:
			self.__curbit = (self.__tagsize * 8) - 1
			self.__tag = self.read_byte()
			for i in range(self.__tagsize - 1):
				self.__tag += self.read_byte() << (8 * (i + 1))

		bit = (self.__tag >> ((self.__tagsize * 8) - 1)) & 0x01
		self.__tag <<= 1
		return bit

	def is_end(self):
		return self.__offset == len(self.__in.getvalue()) and self.__curbit == 1

	def read_byte(self):
		"""read next byte from the stream"""
		result = self.__in.read(1)[0]
		self.__offset += 1
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

	def read_setbits(self, max_, set_=1):
		"""read bits as long as their set or a maximum is reached"""
		result = 0
		while result < max_ and self.read_bit() == set_:
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

	def __literal(self):
		self.read_literal()
		self.__pair = True
		return False

	def __block(self):
		b = self.read_variablenumber()	# 2-
		if b == 2 and self.__pair :	# reuse the same offset
			offset = self.__lastoffset
			length = self.read_variablenumber()	# 2-
		else:
			high = b - 2	# 0-
			if self.__pair:
				high -= 1
			offset = (high << 8) + self.read_byte()
			length = self.read_variablenumber()	# 2-
			length += lengthdelta(offset)
		self.__lastoffset = offset
		self.back_copy(offset, length)
		self.__pair = False
		return False

	def __shortblock(self):
		b = self.read_byte()
		if b <= 1:	# likely 0
			return True
		length = 2 + (b & 0x01)	# 2-3
		offset = b >> 1	# 1-127
		self.back_copy(offset, length)
		self.__lastoffset = offset
		self.__pair = False
		return False

	def __singlebyte(self):
		offset = self.read_fixednumber(4) # 0-15
		if offset:
			self.back_copy(offset)
		else:
			self.read_literal('\x00')
		self.__pair = True

	def do(self):
		"""returns decompressed buffer and consumed bytes counter"""
		self.read_literal()
		while True:
			if self.__functions[self.read_setbits(3)]():
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
	if offset < 0x80 or 0x7D00 <= offset:
		return 2
	elif 0x500 <= offset:
		return 1
	return 0
