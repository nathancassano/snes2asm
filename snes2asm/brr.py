
import wave
from io import BytesIO

def decode(brr_data, rate):
	samples = bytearray()
	last_sample1 = 0
	last_sample2 = 0
	# Process blocks
	for h in range(0, len(brr_data), 9):
		header = brr_data[h]
		shift = header >> 4
		filt = (header >> 2) & 0x3
		# Read samples
		for i in range(h, h+16):
			low_nibble = (h - i & 1) != 0
			sample = (brr_data[i >> 1] & 0xF) if low_nibble else brr_data[i >> 1] >> 4
			# Convert to 4-bit signed
			sample = sample - 8 if sample >= 8 else sample
			# Shifting
			if shift > 12:
				sample = ~0x7FF & sample
			else:
				sample = (sample << shift) >> 1

			# Filtering
			if filt == 1:
				sample += last_sample1 - (last_sample1 >> 4)
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

			sample = clamp(sample)
			last_sample1 = last_sample2
			last_sample2 = sample
			samples.append(sample & 0xFF)
			samples.append((sample >> 8) & 0xFF)
	
	io = BytesIO()
	wav = wave.Wave_write(io)
	wav.setparams((1,2,rate,0,'NONE','not compressed'))
	wav.writeframes(samples)
	io.seek(0)
	return io.read()

def clamp(val):
	if val > 0x7FFF: return 0x7FFF
	if val < -0x7FFF: return -0x7FFF
	return val

def encode(wav_data):
	io = BytesIO(wav_data)
	wav = wave.Wave_read(io)

