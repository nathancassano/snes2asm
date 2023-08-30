# -*- coding: utf-8 -*-

import unittest
from snes2asm.disassembler import OrderedDictRange

class OrderedDictRangeTest(unittest.TestCase):
	
	def setUp(self):
		self.dict = OrderedDictRange({1: 'A', 2: 'B', 3: 'C', 4: 'D'})


	def test_search(self):

		self.assertEqual([(1, 'A')], self.dict.item_range(1,2) )
		self.assertEqual([(2, 'B'), (3, 'C')], self.dict.item_range(2,4) )
		self.assertEqual([], self.dict.item_range(10,20) )

	def test_sort(self):

		self.dict[0] = '#'
		self.dict.sort_keys()
		self.assertEqual([(1, 'A')], self.dict.item_range(1,2) )

if __name__ == '__main__':
    unittest.main()
