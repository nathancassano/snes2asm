# -*- coding: utf-8 -*-

import unittest
from snes2asm.rangetree import RangeTree

class RangeTreeTest(unittest.TestCase):
	
	def setUp(self):
		self.tree = RangeTree()

	def test_search(self):

		self.tree.add(0, 5, 'A')
		self.tree.add(20, 25, 'B')
		self.tree.add(10, 15, 'M')
		self.tree.add(30, 40, 'C')

		self.assertEqual('A', self.tree.find(4) )
		self.assertEqual('B', self.tree.find(22) )
		self.assertEqual('M', self.tree.find(10) )
		self.assertEqual('C', self.tree.find(31) )
		self.assertEqual(None, self.tree.find(41) )
		self.assertEqual('B', self.tree.intersects(17, 26))

		self.assertEqual(['A','M','B','C'], self.tree.items() )

if __name__ == '__main__':
    unittest.main()
