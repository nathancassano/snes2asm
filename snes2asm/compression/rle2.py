# -*- coding: utf-8 -*-

from snes2asm.compression import rle1

def compress(data):
	data1 = bytearray([data[i] for i in range(0,len(data),2)])
	data2 = bytearray([data[i] for i in range(1,len(data),2)])
	out1 = rle1.compress(data1,False)
	out2 = rle1.compress(data2,False)
	return out1 + out2
		
def decompress(data):
	out = bytearray()
	decomp = rle1.decompress(data)
	half = len(decomp)/2
	data1 = decomp[:half]
	data2 = decomp[half:]
	for i in range(0,half):
		out.append(data1[i])
		out.append(data2[i])
	return out
