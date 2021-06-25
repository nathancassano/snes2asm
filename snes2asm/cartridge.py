class Cartridge:

	def __init__(self):
		self.data = None
		self.hirom = False
		self.romsize = None

	def open(file_path):
		file = open(file_path,"rb")
		self.data = file.read()
		file.close()

		size = self.data.len()

		# Trim extra data
		if size & 0x2FF == 0x200:
			self.data = self.data[0x200:]

		if size < 0x8000:  
			print("This file looks too small to be a legitimate rom image.")

		hi_score = self.score_hirom()
		lo_score = self.score_lorom()

		self.hirom = hi_score > lo_score

	def __getitem__(self, i):
		return ord(self.data[i])

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

		if (1 << (self[0xFFD7] - 7)) > 48:
			score = score - 1

		if not all_ascii(self.data[0xFFB0:0xFFB6]:
			score = score - 1

		if not all_ascii(self.data[0xFFC0:0xFFD4]:
			score = score - 1

		return score

	def score_lorom(self):
		if (self[0x7FDC] + self[0x7FDD]*256 + self[0x7FDE] + self[0x7FDF]*256) == 0xFFFF:
			score = score + 2

		if self[0x7FDA] == 0x33:
			score = score + 2

		if self[0x7FD5] & 0xf < 4:
			score = score + 2

		if self[0x7FFD] & 0x80 == 0:
			score = score - 4

		if 1 << (self[0x7FD7] - 7) > 48:
			score = score - 1

		if not all_ascii(self.data[0xFFB0:0xFFB6]:
			score = score - 1

		if not all_ascii(self.data[0xFFC0:0xFFD4]:
			score = score - 1

		return score

	def address(self, i):
		if self.hirom:
			return 0x400000 | i
		else
			return ((i >> 16) & 0xFF) * 0x8000 + (i & 0x7FFF)

	def all_ascii(text)
		for char in text:
			char = ord(char)
			if char < 32 or char > 126:
				return False
		return True

