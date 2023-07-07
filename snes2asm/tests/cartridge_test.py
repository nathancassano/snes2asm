# -*- coding: utf-8 -*-

import unittest
from snes2asm.cartridge import Cartridge

class CartridgeTest(unittest.TestCase):
	
	def setUp(self):
		self.cart = Cartridge()
		self.cart.open('snes2asm/tests/classickong.smc')

	def test_headers(self):

		self.assertEqual(0, self.cart.make_code)
		self.assertEqual("SNES", self.cart.game_code)
		self.assertEqual("\x00\x00\x00\x00\x00\x00\x00", self.cart.fixed)
		self.assertEqual(0, self.cart.expand_ram)
		self.assertEqual(0, self.cart.version)
		self.assertEqual(0, self.cart.sub_type)

		self.assertEqual("Classic Kong Complete", self.cart.title)
		self.assertEqual(0x30, self.cart.map_mode)
		self.assertEqual(0, self.cart.cart_type)
		self.assertEqual(0x8, self.cart.rom_size)
		self.assertEqual(0, self.cart.sram_size)
		self.assertEqual(1, self.cart.country)
		self.assertEqual(0, self.cart.license_code)
		self.assertEqual(0xA2CB, self.cart.comp_check)
		self.assertEqual(0x5D34, self.cart.check_sum)

		# Vectors
		self.assertEqual(0x0, self.cart.nvec_unused)
		self.assertEqual(0x8000, self.cart.nvec_cop)
		self.assertEqual(0x8000, self.cart.nvec_brk)
		self.assertEqual(0x8000, self.cart.nvec_abort)
		self.assertEqual(0x8091, self.cart.nvec_nmi)
		self.assertEqual(0x0, self.cart.nvec_reset)
		self.assertEqual(0x8000, self.cart.nvec_irq)
		self.assertEqual(0x0, self.cart.evec_unused)
		self.assertEqual(0x8000, self.cart.evec_cop)
		self.assertEqual(0x0, self.cart.evec_unused2)
		self.assertEqual(0x8000, self.cart.evec_abort)
		self.assertEqual(0x8000, self.cart.evec_nmi)
		self.assertEqual(0x80B7, self.cart.evec_reset)
		self.assertEqual(0x8000, self.cart.evec_irq)

if __name__ == '__main__':
    unittest.main()
