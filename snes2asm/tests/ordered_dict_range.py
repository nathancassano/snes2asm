import unittest
from snes2asm.disassembler import OrderedDictRange

class OrderedDictRangeTest(unittest.TestCase):
	
	def setUp(self):
		self.dict = OrderedDictRange({1: 'A', 2: 'B', 3: 'C', 4: 'D'})

	def test_search(self):

		self.assertEquals([(1, 'A')], self.dict.item_range(1,2) )
		self.assertEquals([(2, 'B'), (3, 'C')], self.dict.item_range(2,4) )
		self.assertEquals([], self.dict.item_range(10,20) )

if __name__ == '__main__':
    unittest.main()
