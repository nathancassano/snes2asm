# -*- coding: utf-8 -*-

def compress(data):
	# Find first unused byte value in data
	tag = next((d for d in range(0,255) if d not in data))
	out = bytearray([tag])
	last = data[0]
	count = 0
	i = 0
	while i <= len(data):
		if i < len(data):
			c = data[i]
		if c == last and i < len(data) and count < 254:
			count += 1
		elif count > 1:
			out += bytearray([last,tag,count])
			count = 1
		elif last == tag:
			out += bytearray([last,tag,1])
		else:
			out.append(last)
		last = c
		i += 1
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
			out += bytearray([last] * (count - 1))
		else:
			out.append(c)
			last = c
		i += 1
	return out
