# -*- coding: utf-8 -*-

import unittest
from tile2bin.application import App

class ApplicationTest(unittest.TestCase):
	
	def setUp(self):
		self.app = App({})

	def test_headers(self):
		pass
		#self.assertEqual(0, self.cart.make_code)

if __name__ == '__main__':
	unittest.main()
