# -*- coding: utf-8 -*-

from itertools import groupby

def compress(data):
	# Find first unused byte value in data
	tag = next((d for d in range(0,255) if d not in data))
	out = bytearray([tag])

	# Process grouped data runs
	for val, item in groupby(data):
		count = len(list(item))
		if count > 2:
			out += bytearray([val,tag,count-1])
		else:
			out += bytearray([val]*count)

	# Mark end of rle
	out += bytearray([tag,0])
	return out	

def decompress(data):
	out = bytearray()
	tag = data[0]
	last = tag
	i = 1
	while i < len(data):
		c = data[i]
		if c == tag:
			i += 1
			count = data[i]
			# End of rle found
			if count == 0:
				break
			out += bytearray([last] * count)
		else:
			out.append(c)
			last = c
		i += 1
	return out
