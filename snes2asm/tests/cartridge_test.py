import unittest
import pdb 
from snes2asm.cartridge import Cartridge

class CartridgeTest(unittest.TestCase):
	
	def setUp(self):
		self.cart = Cartridge()
		self.cart.open('snes2asm/tests/classickong.smc')

	def test_headers(self):

		self.assertEquals(0, self.cart.make_code)
		self.assertEquals("SNES", self.cart.game_code)
		self.assertEquals("\x00\x00\x00\x00\x00\x00\x00", self.cart.fixed)
		self.assertEquals(0, self.cart.expand_ram)
		self.assertEquals(0, self.cart.version)
		self.assertEquals(0, self.cart.sub_type)

		self.assertEquals("Classic Kong Complete", self.cart.title)
		self.assertEquals(0x30, self.cart.map_mode)
		self.assertEquals(0, self.cart.cart_type)
		self.assertEquals(0x8, self.cart.rom_size)
		self.assertEquals(0, self.cart.sram_size)
		self.assertEquals(1, self.cart.country)
		self.assertEquals(0, self.cart.license_code)
		self.assertEquals(0, self.cart.rom_mask)
		self.assertEquals(0xA2CB, self.cart.comp_check)
		self.assertEquals(0x5D34, self.cart.check_sum)

		# Vectors
		self.assertEquals(0x0, self.cart.nvec_unused)
		self.assertEquals(0x8000, self.cart.nvec_cop)
		self.assertEquals(0x8000, self.cart.nvec_brk)
		self.assertEquals(0x8000, self.cart.nvec_abort)
		self.assertEquals(0x8091, self.cart.nvec_nmi)
		self.assertEquals(0x0, self.cart.nvec_reset)
		self.assertEquals(0x8000, self.cart.nvec_irq)
		self.assertEquals(0x0, self.cart.evec_unused)
		self.assertEquals(0x8000, self.cart.evec_cop)
		self.assertEquals(0x0, self.cart.evec_unused2)
		self.assertEquals(0x8000, self.cart.evec_abort)
		self.assertEquals(0x8000, self.cart.evec_nmi)
		self.assertEquals(0x80B7, self.cart.evec_reset)
		self.assertEquals(0x8000, self.cart.evec_irq)

if __name__ == '__main__':
    unittest.main()
