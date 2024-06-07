def compress(data):
	return lz2_compress(data).do()

def decompress(data):
	return lz2_decompress(data).do()

class lz2_compress:
	def __init__(self, data):
		self._in = data
		self._out = bytearray()

	def do(self):
		raise NotImplementedError
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
		self._out += bytearray(range(val, val + self._length))
		self._offset += 1

	def _repeat(self):
		start = self._in[self._offset] | (self._in[self._offset+1] << 8)
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
		while self._offset < len(self._in)
			self._command()
		return self._out
