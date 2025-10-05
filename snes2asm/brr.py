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

	# Read all frames as raw bytes
	raw_samples = wav.readframes(wav.getnframes())

	# Convert to 16-bit signed samples
	samples = []
	for i in range(0, len(raw_samples), 2):
		sample = raw_samples[i] | (raw_samples[i+1] << 8)
		# Convert to signed
		if sample >= 0x8000:
			sample -= 0x10000
		# Scale down from 16-bit to 15-bit range
		samples.append(sample >> 1)

	brr_data = bytearray()
	last_samples = [[0, 0] for _ in range(4)]  # [last_sample1, last_sample2] for each filter

	# Process 16 samples at a time (one BRR block)
	for block_start in range(0, len(samples), 16):
		block = samples[block_start:block_start+16]
		if len(block) < 16:
			# Pad final block with zeros
			block.extend([0] * (16 - len(block)))

		# Check if this is the last block
		is_last_block = (block_start + 16 >= len(samples))

		# Find best filter and shift for this block
		best_error = float('inf')
		best_filter = 0
		best_shift = 0
		best_nibbles = None

		for filt in range(4):
			for shift in range(13):
				error = 0
				nibbles = []
				test_last1 = last_samples[filt][0]
				test_last2 = last_samples[filt][1]

				for sample in block:
					# Predict sample using filter
					predicted = 0
					if filt == 1:
						predicted = test_last2 - (test_last2 >> 4)
					elif filt == 2:
						predicted = (test_last2 << 1) + ((-(test_last2 * 3)) >> 5) - test_last1 + (test_last1 >> 4)
					elif filt == 3:
						predicted = (test_last2 << 1) + ((-(test_last2 * 13)) >> 6) - test_last1 + ((test_last1 * 3) >> 4)

					# Calculate delta
					delta = sample - predicted

					# Quantize delta to 4-bit range with shift
					if shift > 12:
						quantized = 0
					else:
						quantized = (delta << 1) >> shift

					# Clamp to 4-bit signed range (-8 to 7)
					if quantized > 7:
						quantized = 7
					elif quantized < -8:
						quantized = -8

					nibbles.append(quantized & 0xF)

					# Reconstruct sample for filter prediction
					if shift > 12:
						reconstructed_delta = 0
					else:
						# Sign-extend 4-bit value
						signed_nibble = quantized if quantized < 8 else quantized - 16
						reconstructed_delta = (signed_nibble << shift) >> 1

					reconstructed = predicted + reconstructed_delta
					reconstructed = clamp(reconstructed)

					# Track error
					error += abs(sample - reconstructed)

					test_last1 = test_last2
					test_last2 = reconstructed

				if error < best_error:
					best_error = error
					best_filter = filt
					best_shift = shift
					best_nibbles = nibbles

		# Write BRR block header
		header = (best_shift << 4) | (best_filter << 2)
		# Set end and loop flags on the last block
		if is_last_block:
			header |= 0x03  # Set both loop (bit 1) and end (bit 0) flags
		brr_data.append(header)

		# Write BRR block samples (16 nibbles = 8 bytes)
		for i in range(0, 16, 2):
			byte = (best_nibbles[i] << 4) | best_nibbles[i+1]
			brr_data.append(byte)

		# Update last samples for chosen filter
		test_last1 = last_samples[best_filter][0]
		test_last2 = last_samples[best_filter][1]

		for i, nibble in enumerate(best_nibbles):
			# Reconstruct using chosen filter
			predicted = 0
			if best_filter == 1:
				predicted = test_last2 - (test_last2 >> 4)
			elif best_filter == 2:
				predicted = (test_last2 << 1) + ((-(test_last2 * 3)) >> 5) - test_last1 + (test_last1 >> 4)
			elif best_filter == 3:
				predicted = (test_last2 << 1) + ((-(test_last2 * 13)) >> 6) - test_last1 + ((test_last1 * 3) >> 4)

			# Decode nibble
			signed_nibble = nibble if nibble < 8 else nibble - 16
			if best_shift > 12:
				delta = 0
			else:
				delta = (signed_nibble << best_shift) >> 1

			reconstructed = clamp(predicted + delta)
			test_last1 = test_last2
			test_last2 = reconstructed

		# Update all filters' last samples
		for f in range(4):
			last_samples[f] = [test_last1, test_last2]

	return bytes(brr_data)

def clamp(val):
	if val > 0x7FFF: return 0x7FFF
	if val < -0x7FFF: return -0x7FFF
	return val
