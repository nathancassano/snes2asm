import struct

class Cartridge:

	def __init__(self, options={}):
		self.options = options
		self.data = []
		self.hirom = False
		self.fastrom = False
		self.base_address = 0x8000
		self.header = 0

    # Data indexing and slicing
	def __getitem__(self, i):
		if isinstance(i, slice):
			return [ ord(self.data[ir]) for ir in range(i.start, i.stop) ]
		else:
			return ord(self.data[i])

	# Open rom file
	def open(self,file_path):
		file = open(file_path,"rb")
		data = file.read()
		file.close()
		self.set(data)

    # Assign cart data
	def set(self, data):

		self.data = data
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

		self.extended = size > 0x400000

		self.header = 0x400000 if self.extended else 0

		if self.options.get('hirom'):
			self.hirom = True
		elif self.options.get('lorom'):
			self.hirom = False
		else:
			hi_score = self.score_hirom()
			lo_score = self.score_lorom()

			self.hirom = hi_score > lo_score

		if self.options.get('fastrom'):
			self.fastrom = True
		elif self.options.get('slowrom'):
			self.fastrom = False
		else:
			# Auto-detect
			self.fastrom = (self[0xFFD5 if self.hirom else 0x7FD5] & 0x30) != 0

		self.base_address = 0x400000 if self.extended else 0x008000

		self.header = self.header + (0x0ffb0 if self.hirom else 0x07fb0)

		self.parse_header()

		type = "Ext" if self.extended else ""
		type = type + ( "HiROM" if self.hirom else "LoROM")
		tv = "PAL" if self.country >= 2 and self.country <= 12 else "NTSC"
		print("Detected: %s[0x%x] ROMID:%s Type:%s TV:%s CheckSum:%04x" % (type, len(self.data), self.title, self.map_type(), tv, self.check_sum))

	def parse_header(self):
		(self.make_code, self.game_code, self.fixed, self.expand_ram, self.version, self.sub_type, self.title, self.map_mode, self.cart_type, self.rom_size, self.sram_size, self.country, self.license_code, self.rom_mask, self.comp_check, self.check_sum) = struct.unpack("H4s7s3b21s7b2H", self.data[self.header:self.header+48])

		(self.nvec_unused, self.nvec_cop, self.nvec_brk, self.nvec_abort, self.nvec_nmi, self.nvec_reset, self.nvec_irq, self.evec_unused, self.evec_cop, self.evec_unused2, self.evec_abort, self.evec_nmi, self.evec_reset, self.evec_irq) = struct.unpack("I6HI6H", self.data[self.header+48:self.header+80])

	def map_type(self):
		type = ["ROM", "ROM+RAM", "ROM+RAM+BAT"]
		return type[self.cart_type]

    # Translate rom position to address
	def address(self, i):
		if self.hirom:
			return self.base_address + i
		else:
			return (((i & 0xFF8000) << 1) + (i & 0x7FFF)) + self.base_address

	# Translate address to rom position
	def index(self, address):
		if address < 0x8000:
			return -1
		# LoROM
		if not self.hirom:
			if address & 0x8000 == 0:
				return -1
			address = (((address & 0x7F0000) >> 1) + (address & 0x7FFF))
		else:
			address = address & 0x7FFFFF
		if address > self.size():
			return -1
		mask = self.size() - 1
		return address & mask

	def bank_size(self):
		return 0x10000 if self.hirom else 0x8000

	def bank_count(self):
		return len(self.data) / self.bank_size()

	def size(self):
		return len(self.data)

	def score_hirom(self):
		score = 0
		if (self[self.header + 0xFFDC] + self[self.header + 0xFFDD]*256 + self[self.header + 0xFFDE] + self[self.header + 0xFFDF]*256) == 0xFFFF:
			score = score + 2

		if self[self.header + 0xFFDA] == 0x33:
			score = score + 2

		if self[self.header + 0xFFD5] & 0xf < 4:
			score = score + 2

		if self[self.header + 0xFFFD] & 0x80 == 0:
			score = score - 4

		if (1 << abs(self[self.header + 0xFFD7] - 7)) > 48:
			score = score - 1

		if not all_ascii(self.data[self.header + 0xFFB0: self.header + 0xFFB6]):
			score = score - 1

		if not all_ascii(self.data[self.header + 0xFFC0:self.header + 0xFFD4]):
			score = score - 1

		return score

	def score_lorom(self):
		score = 0
		if (self[self.header + 0x7FDC] + self[self.header + 0x7FDD]*256 + self[self.header + 0x7FDE] + self[self.header + 0x7FDF]*256) == 0xFFFF:
			score = score + 2

		if self[self.header + 0x7FDA] == 0x33:
			score = score + 2

		if self[self.header + 0x7FD5] & 0xf < 4:
			score = score + 2

		if self[self.header + 0x7FFD] & 0x80 == 0:
			score = score - 4

		if 1 << abs(self[self.header + 0x7FD7] - 7) > 48:
			score = score - 1

		if not all_ascii(self.data[self.header + 0xFFB0:self.header + 0xFFB6]):
			score = score - 1

		if not all_ascii(self.data[self.header + 0xFFC0:self.header + 0xFFD4]):
			score = score - 1

		return score


def all_ascii(text):
	for char in text:
		char = ord(char)
		if char < 32 or char > 126:
			return False
	return True

