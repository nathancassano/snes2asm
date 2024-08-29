# -*- coding: utf-8 -*-

def compress(data):
	out = bytearray()
	i = 0
	anchor = 0
	end = len(data) - 5
	while i < len(data):
		# Find the longest match
		match_length = 0
		match_offset = 0
		for j in range(0, i):
			length = 0
			while i + length < end and data[j + length] == data[i + length]:
				length += 1
			if length > match_length:
				match_length = length
				match_offset = j + 1

		literal_length = i - anchor

		# If the match is too short
		if match_length < 4:
			i += 1
			if i < len(data):
				continue
			# End of data reached
			literal_length = len(data) - anchor
			token = (min(15, literal_length) << 4)
			match_length = -1
		else:
			match_length -= 4
			token = (min(15, literal_length) << 4) | min(15, match_length)

		out.append(token)

		# Encode literals
		if literal_length >= 15:
			n = literal_length - 15
			while n >= 0xFF:
				out.append(0xFF)
				n -= 0xFF
			out.append(n)

		out.extend(data[anchor:anchor + literal_length])

		# Encode match
		if match_length >= 0:
			out.append(match_offset & 0xFF)
			out.append((match_offset >> 8) & 0xFF)

			if match_length >= 15:
				n = match_length - 15
				while n >= 0xFF:
					out.append(0xFF)
					n -= 0xFF
				out.append(n)
			i += match_length + 4
		anchor = i
	return out

def decompress(data):
	out = bytearray()
	i = 0
	while i < len(data):
		token = data[i]
		i += 1
	
		literal_length = token >> 4
		match_length = token & 0xF
	
		if literal_length > 0:
			if literal_length == 0xF:
				while True:
					ext_direct = data[i]
					i += 1
					literal_length += ext_direct
					if data[offset] != 0xFF: break
			# Copy literal_length
			end = i + literal_length
			out += data[i:end]
			i = end
	
		if i >= len(data):
			break
	
		offset = (data[i] | (data[i+1] << 8)) - 1
		i += 2

		if match_length == 0xF:
			while True:
				ext_length = data[i]
				i += 1
				match_length += ext_length
				if ext_length != 0xFF: break
		match_length += 4
		for x in range(offset, offset + match_length):
			out.append(out[x])
	return out