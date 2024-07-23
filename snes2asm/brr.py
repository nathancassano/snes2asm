# -*- coding: utf-8 -*-

import wave
from io import BytesIO

def decode(brr_data, rate=32000):
	samples = bytearray()
	last_sample1 = 0
	last_sample2 = 0
	# Process blocks
	for h in range(0, len(brr_data), 9):
		header = brr_data[h]
		shift = header >> 4
		filt = (header >> 2) & 0x3
		h += 1
		# Read block samples
		for i in range(0, 16):
			low_nibble = (i & 1) != 0
			i = h + (i >> 1)
			sample = (brr_data[i] & 0xF) if low_nibble else brr_data[i] >> 4
			# Convert to 4-bit signed
			sample = sample - 16 if sample >= 8 else sample
			# Shifting
			if shift > 12:
				sample = ~0x7FF & sample
			else:
				sample = (sample << shift) >> 1
			sample = sample_filter(sample, filt, last_sample1, last_sample2)
			sample = clamp(sample)
			last_sample1 = last_sample2
			last_sample2 = sample
			sample = sample * 2
			samples.append(sample & 0xFF)
			samples.append((sample >> 8) & 0xFF)
	io = BytesIO()
	wav = wave.Wave_write(io)
	wav.setparams((1,2,rate,0,'NONE','not compressed'))
	wav.writeframes(samples)
	io.seek(0)
	return io.read()

def sample_filter(sample, filt, last_sample1, last_sample2):
	# Filtering
	if filt == 0:
		pass
	elif filt == 1:
		sample += last_sample2 - (last_sample2 >> 4)
	elif filt == 2:
		sample += last_sample2 << 1
		sample += -(last_sample2 + (last_sample2 << 1)) >> 5
		sample += -last_sample1
		sample += last_sample1 >> 4
	elif filt == 3:
		sample += last_sample2 << 1
		sample += -(last_sample2 + (last_sample2 << 2) + (last_sample2 << 3)) >> 6
		sample += -last_sample1
		sample += (last_sample1 + (last_sample1 << 1)) >> 4
	return sample


def encode(wav_data):
	io = BytesIO(wav_data)
	wav = wave.Wave_read(io)

	if wav.getnchannels() != 1:
		raise ValueError('Audio sample must be mono')

	if wav.getsampwidth() != 2:
		raise ValueError('Audio sample must be 16-bit')

	frames = (len(wav_data) - 44) / 4
	
	samples = wav.readframes(frames)
	brr_data = bytearray()

	last_sample1 = 0
	last_sample2 = 0
	
	for h in range(0, len(samples), 8):

		block = []
		bit_saturate = 0
		for i in range(h, h+8):
			sample = samples[i][0] | samples[i][1] << 8
			bit_saturate |= sample
			block.append(sample)

			# Fitlers
			for f in range(0, 4):
				if f == 0:
					pass
				else:
					delta = sample_filter(sample, f, last_sample1[f], last_sample2[f])
			
			last_sample1 = last_sample2
			last_sample2 = sample
		high_bit = msb(sample)

def msb(num):
	if num < 0: num = ~num
	bc = 0
	while num != 0:
		num = num >> 1
		bc += 1
	return bc

def lsb(num):
	if num < 0: num = ~num
	bc = 0
	while num & 1 == 0:
		num = num >> 1
		bc += 1
	return bc

def clamp(val):
	if val > 0x7FFF: return 0x7FFF
	if val < -0x7FFF: return -0x7FFF
	return val

		
