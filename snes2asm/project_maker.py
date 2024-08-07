# -*- coding: utf-8 -*-

import os
import shutil
from string import Template
from snes2asm import template as template_path
from snes2asm.decoder import ansi_escape

class ProjectMaker:

	def __init__(self, cart, disasm):
		self.cart = cart
		self.disasm = disasm

	def output(self, dir):
		print("Writing project files...")
		if not os.path.isdir(dir):
			os.mkdir(dir)

		self.create_header(dir)
		self.create_makefile(dir)
		self.bank_code(dir)
		self.copy_files(dir)

		# Write support code
		filename = "%s/constants.asm" % dir
		f = open(filename, 'w')
		f.write(self.disasm.support_code())
		f.close()

		# Write bank assembly code
		for bank in range(0, self.cart.bank_count()):
			code = self.disasm.bank_code(bank)
			filename = "%s/bank%d.asm" % (dir, bank)
			f = open(filename, 'w')
			f.write(code)
			f.close()


		# Write decoder files
		for decoder in self.disasm.decoders.items():
			for file, content in decoder.files.items():
				filename = "%s/%s" % (dir, file)
				mode = 'w' if type(content) == str else 'wb'
				f = open(filename, mode)
				f.write(content)
				f.close()

		# Write support decoder files
		for decoder in self.disasm.support_decoders:
			for file, content in decoder.files.items():
				filename = "%s/%s" % (dir, file)
				f = open(filename, 'wb')
				f.write(content)
				f.close()

	def copy_files(self, dir):
		files = ['snes.asm', 'linkfile']
		for f in files:
			shutil.copyfile("%s/%s" % (template_path.__path__[0], f), "%s/%s" % (dir, f) )

	def bank_code(self, dir):
		f = open("%s/main.s" % template_path.__path__[0])
		main_temp = f.read()
		f.close()
		temp = PercentTemplate(main_temp)
		bank_includes = "\n".join([".include \"bank%d.asm\"" % i for i in range(0, self.cart.bank_count())])
		main = temp.substitute(banks=bank_includes)
		f = open("%s/main.s" % dir, 'w')
		f.write(main)
		f.close()

	def create_makefile(self, dir):
		f = open("%s/Makefile" % template_path.__path__[0])
		makefile_temp = f.read()
		f.close()

		compress_targets = self.disasm.get_compress_targets()

		encode_files = " ".join([t[0] for t in compress_targets])
		encode_targets = ''
		for (target_file, source_file, compress_type) in compress_targets:
			encode_targets += "%s: %s\n\t$(PACKER) pack -x %s -o $@ $<\n\n" % (target_file, source_file, compress_type);
		temp = PercentTemplate(makefile_temp)
		makefile = temp.safe_substitute(encode_files=encode_files, endcode_targets=encode_targets)
		f = open("%s/Makefile" % dir, 'w')
		f.write(makefile)
		f.close()

	def create_header(self, dir):
		f = open("%s/hdr.asm" % template_path.__path__[0])
		hdr_temp = f.read()
		f.close()
		temp = PercentTemplate(hdr_temp)
		rom_speed = 'FASTROM' if self.cart.fastrom else 'SLOWROM'
		if self.cart.extended:
			rom_map = 'EXHIROM' if self.cart.hirom else 'EXLOROM ; unsupported map type'
		else:
			rom_map = 'HIROM' if self.cart.hirom else 'LOROM'
		hdr = temp.substitute(
			title=ansi_escape(self.cart.title[0:21].ljust(21)),
			bank_size="%06X" % self.cart.bank_size(),
			slot_size="0" if self.cart.hirom else "8000",
			rom_banks=self.cart.bank_count(),
			rom_speed=rom_speed,
			rom_map=rom_map,
			game_code=ansi_escape(self.cart.game_code),
			empty_fill="%02X" % self.cart.empty_fill,
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
			nvec_reset=self.get_vector(self.cart.nvec_reset),
			evec_cop=self.get_vector(self.cart.evec_cop),
			evec_abort=self.get_vector(self.cart.evec_abort),
			evec_nmi=self.get_vector(self.cart.evec_nmi),
			evec_reset=self.get_vector(self.cart.evec_reset),
			evec_irq=self.get_vector(self.cart.evec_irq),
			evec_unused2=self.get_vector(self.cart.evec_unused2)
		)
		filename = "%s/hdr.asm" % dir
		f = open(filename, 'w')
		f.write(hdr)
		f.close()

	def get_vector(self, address):
		if address >= 0x8000 and self.disasm.valid_label(address - 0x8000) and not self.disasm.no_label:
			return self.disasm.label_name(address - 0x8000)
		else:
			return "$%04X" % address

class PercentTemplate(Template):
	delimiter = '%'

