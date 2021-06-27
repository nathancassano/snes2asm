
import pdb

class Cartridge:

	def __init__(self, options={}):
		self.options = options
		self.data = []
		self.hirom = False
		self.romsize = None
		self.base_address = 0

	def __getitem__(self, i):
		return ord(self.data[i])

	def open(self,file_path):
		file = open(file_path,"rb")
		self.data = file.read()
		file.close()

		size = len(self.data)

		# Trim extra data
		if size & 0x2FF == 0x200:
			self.data = self.data[0x200:]
			size = size - 0x200

		if size < 0x8000:  
			print("This file looks too small to be a legitimate rom image.")
			exit(1)

		if size & 0xFFFF != 0:
			print("This file looks the wrong size to be a legitimate rom image.")
			exit(1)

		if self.options.hirom:
			self.hirom = True
		elif self.options.lorom:
			self.hirom = False
		else:
			hi_score = self.score_hirom()
			lo_score = self.score_lorom()

			self.hirom = hi_score > lo_score

		if self.options.shadow:
			shadow = True
		elif self.options.noshadow:
			shadow = False
		else:
			# Auto-detect
			shadow = (self[0xFFD5 if self.hirom else 0x7FD5] & 0x30) != 0

		if shadow:
			self.base_address = 0xC00000 if self.hirom else 0x808000
		else:
			self.base_address = 0x400000 if self.hirom else 0x008000

	def address(self, i):
		if self.hirom:
			return self.base_address | i
		else:
			return (((i & 0xFF8000) << 1) + (i & 0x7FFF)) + self.base_address

	def score_hirom(self):
		score = 0
		if (self[0xFFDC] + self[0xFFDD]*256 + self[0xFFDE] + self[0xFFDF]*256) == 0xFFFF:
			score = score + 2

		if self[0xFFDA] == 0x33:
			score = score + 2

		if self[0xFFD5] & 0xf < 4:
			score = score + 2

		if self[0xFFFD] & 0x80 == 0:
			score = score - 4

		if (1 << abs(self[0xFFD7] - 7)) > 48:
			score = score - 1

		if not all_ascii(self.data[0xFFB0:0xFFB6]):
			score = score - 1

		if not all_ascii(self.data[0xFFC0:0xFFD4]):
			score = score - 1

		return score

	def score_lorom(self):
		score = 0
		if (self[0x7FDC] + self[0x7FDD]*256 + self[0x7FDE] + self[0x7FDF]*256) == 0xFFFF:
			score = score + 2

		if self[0x7FDA] == 0x33:
			score = score + 2

		if self[0x7FD5] & 0xf < 4:
			score = score + 2

		if self[0x7FFD] & 0x80 == 0:
			score = score - 4

		if 1 << abs(self[0x7FD7] - 7) > 48:
			score = score - 1

		if not all_ascii(self.data[0xFFB0:0xFFB6]):
			score = score - 1

		if not all_ascii(self.data[0xFFC0:0xFFD4]):
			score = score - 1

		return score


def all_ascii(text):
	for char in text:
		char = ord(char)
		if char < 32 or char > 126:
			return False
	return True

