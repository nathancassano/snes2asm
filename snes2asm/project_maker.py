# -*- coding: utf-8 -*-

import os
import shutil
from string import Template

class ProjectMaker:

	def __init__(self, cart, disasm):
		self.cart = cart
		self.disasm = disasm

	def output(self, dir):
		print("Writing project files...")
		if not os.path.isdir(dir):
			os.mkdir(dir)

		self.create_header(dir)
		self.copy_files(dir)

		# Write decoder files
		for decoder in self.disasm.decoders.items():
			for file, content in decoder.files.items():
				filename = "%s/%s" % (dir, file)
				f = open(filename, 'wb')
				f.write(content)
				f.close()

		# Write main assembly code
		filename = "%s/game.asm" % dir
		f = open(filename, 'w')
		f.write(self.disasm.assembly())
		f.close()

	def copy_files(self, dir):
		files = ['Makefile','clean.bat','compile.bat', 'snes.asm', 'main.s', 'linkfile']
		for f in files:
			shutil.copyfile("snes2asm/template/" + f, "%s/%s" % (dir, f) )

	def create_header(self, dir):
		f = open('snes2asm/template/hdr.asm')
		hdr_temp = f.read()
		f.close()
		template = PercentTemplate(hdr_temp)
		rom_speed = 'FASTROM' if self.cart.fastrom else 'SLOWROM'
		if self.cart.extended:
			rom_map = 'EXHIROM' if self.cart.hirom else 'EXLOROM ; unsupported map type'
		else:
			rom_map = 'HIROM' if self.cart.hirom else 'LOROM'
		hdr = template.substitute(
			title=self.cart.title[0:21].ljust(21),
			bank_size="%06X" % self.cart.bank_size(),
			slot_size="0" if self.cart.hirom else "8000",
			rom_banks=len(self.cart.data) / self.cart.bank_size(),
			rom_speed=rom_speed,
			rom_map=rom_map,
			cart_type="%02X" % self.cart.cart_type,
			rom_size="%02X" % self.cart.rom_size,
			sram_size="%02X" % self.cart.sram_size,
			country="%02X" % self.cart.country,
			license_code="%02X" % self.cart.license_code,
			version="%02X" % self.cart.version,
			nvec_cop=self.get_vector(self.cart.nvec_cop),
			nvec_brk=self.get_vector(self.cart.nvec_brk),
			nvec_abort=self.get_vector(self.cart.nvec_abort),
			nvec_nmi=self.get_vector(self.cart.nvec_nmi),
			nvec_irq=self.get_vector(self.cart.nvec_irq),
			evec_cop=self.get_vector(self.cart.evec_cop),
			evec_abort=self.get_vector(self.cart.evec_abort),
			evec_nmi=self.get_vector(self.cart.evec_nmi),
			evec_reset=self.get_vector(self.cart.evec_reset),
			evec_irq=self.get_vector(self.cart.evec_irq)
		)
		filename = "%s/hdr.asm" % dir
		f = open(filename, 'w')
		f.write(hdr)
		f.close

	def get_vector(self, address):
		if address >= 0x8000 and self.disasm.valid_label(address - 0x8000):
			return "L%06X" % (address - 0x8000)
		else:
			return "$%04X" % address

class PercentTemplate(Template):
	delimiter = '%'

