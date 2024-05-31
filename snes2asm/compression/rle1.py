# -*- coding: utf-8 -*-

from itertools import groupby	

def compress(data):
	compress.out = bytearray()
	compress.direct = bytearray()

	def write_direct_data():
		if len(compress.direct) > 0:
			# Write direct data command
			dlen = len(compress.direct) - 1
			compress.out += bytearray([dlen >> 8, dlen & 0xFF]) + compress.direct
			compress.direct = bytearray()

	# Process grouped data runs
	for val, item in groupby(data):
		count = len(list(item))
		if count > 1:
			write_direct_data()
			step = 0x80 if val == 0xFF else 0x8000
			# Write repeating command
			for i in range(count,0,-step):
				dlen = (step if i >= step else i) - 1
				compress.out += bytearray([0x80 | (dlen>> 8), dlen & 0xFF, val])
		else:
			compress.direct.append(val)

	write_direct_data()

	# Write terminator
	compress.out += bytearray([0xFF, 0xFF])

	return compress.out

def decompress(data):
	out = bytearray()
	stream = iter(data)
	for d in stream:
		header = d << 8 | next(stream)
		if header == 0xFFFF:
			break
		count = (0x7FFF & header) + 1
		# Repeat command
		if d & 0x80 != 0:
			out += bytearray([next(stream)] * count)
		# Direct copy coomand
		else:
			for i in range(0,count):
				out.append(next(stream))
	return out
