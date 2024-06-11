from functools import reduce

def compress(data):
	return lz2_compress(data).do()

def decompress(data):
	return lz2_decompress(data).do()

class lz2_compress:

	DIRECT_COPY = 0
	FILL_BYTE = 1
	FILL_WORD = 2
	FILL_INC = 3
	REPEAT = 4

	def __init__(self, data):
		self._in = data
		self._offset = 0
		self._direct = bytearray()
		self._out = bytearray()

	def _rle8(self):
		val = self._in[self._offset]

		index = self._offset + 1
		while index < len(self._in) and val == self._in[index]:
			index += 1
		return (self.FILL_BYTE, index - self._offset, val)

	def _rle16(self):
		if self._offset + 2 >= len(self._in):
			return (2, 0, 0)
		val1 = self._in[self._offset]
		val2 = self._in[self._offset+1]

		index = self._offset + 2
		while index < len(self._in) and val1 == self._in[index] and val2 == self._in[index+1]:
			index += 2
		length = index - self._offset
		length = length if length > 2 else 0
		return (self.FILL_WORD, length, bytearray([val1, val2]))

	def _increment_fill(self):
		val = self._in[self._offset]
		index = self._offset
		while index < len(self._in) and val == self._in[index]:
			val = (val + 1) & 0xFF
			index += 1
		return (self.FILL_INC, index - self._offset, self._in[self._offset])


	def _repeat(self):
		max_length = 0
		max_index = 0

		for index in range(0, self._offset):
			offset = self._offset
			while offset < len(self._in) and self._in[index] == self._in[offset]:
				offset += 1
				index += 1
			length = offset - self._offset

			if length > max_length:
				max_length = length
				max_index = index - length

		return (self.REPEAT, max_length, bytearray([max_index & 0xFF, max_index >> 8]))

	def _write_direct_copy(self):
		if len(self._direct) > 0:
			self._write_command(DIRECT_COPY, len(self._direct), self._direct)
			self._direct = bytearray()

	def _write_command(self, command, length, val):
		if command == self.FILL_WORD:
			length = length >> 1
		length -= 1
		if type(val) != bytearray:
			val = bytearray([val])
		# Long command
		if length > 0x1F:
			header = 0xE0 | (command << 2) | length >> 8
			self._out += bytearray([header, length & 0xFF]) + val
		else:
			header = command << 5 | length
			self._out += bytearray([header]) + val

	def do(self):
		while self._offset < len(self._in):
			# Run all encoding candidates
			algs = [self._rle16(), self._rle8(),self._increment_fill(),self._repeat()]
			# Select longest running algorithm
			(command, length, val) = reduce(lambda a, b: a if a[1] > b[1] else b, algs)
			if length > 2:
				self._write_direct_copy()
				self._write_command(command, length, val)
			else:
				self._direct.append(self._in[self._offset])
				length = 1

			self._offset += length
		self._write_direct_copy()

		# Terminate
		self._out.append(0xFF)
		return self._out

class lz2_decompress:
	def __init__(self, data):
		self._in = data
		self._offset = 0
		self._length = 0
		self._out = bytearray()
		self._functions = [self._direct_copy, self._fill_byte, self._fill_word, self._inc_fill, self._repeat, self._noop, self._noop, self._long_command]

	def _direct_copy(self):
		end = self._offset + self._length
		self._out += self._in[self._offset:end]
		self._offset += self._length

	def _fill_byte(self):
		val = self._in[self._offset]
		self._out += bytearray([val] * self._length)
		self._offset += 1

	def _fill_word(self):
		val1 = self._in[self._offset]
		val2 = self._in[self._offset+1]
		self._out += bytearray([val1,val2] * self._length)
		self._offset += 2

	def _inc_fill(self):
		val = self._in[self._offset]
		self._out += bytearray([x & 0xFF for x in range(val, val + self._length)])
		self._offset += 1

	def _repeat(self):
		start = (self._in[self._offset] | (self._in[self._offset+1] << 8))
		end = start + self._length
		self._out += self._out[start:end]
		self._offset += 2
	
	def _noop(self):
		pass

	def _command(self):
		chunk = self._in[self._offset]
		# Terminate
		if chunk == 0xFF:
			self._offset = len(self._in)
			return
		# Run command
		command = (chunk & 0xE0) >> 5
		self._length = chunk & 0x1F
		if command != 0x7:
			self._length += 1
		self._offset += 1
		self._functions[command]()

	def _long_command(self):
		command = self._length >> 2
		ext_length = self._in[self._offset]
		self._length = ((self._length & 0x3) << 8 | ext_length) + 1
		self._offset += 1
		self._functions[command]()

	def do(self):
		while self._offset < len(self._in):
			self._command()
		return self._out
