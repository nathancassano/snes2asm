# -*- coding: utf-8 -*-

import unittest
import os
import shutil
from snes2asm import main

class ProjectTest(unittest.TestCase):
	
	def test_run(self):
		directory = os.path.dirname(__file__)
		path = os.path.join(directory, 'classickong.smc')
		conf = os.path.join(directory, 'classickong.yaml')
		out = os.path.join(directory, 'project')

		# ./snes2asm -o project -c classickong.yaml classickong.smc
		main(['snes2asm', '-o', out, '-c', conf,  path])
		shutil.rmtree(out)

if __name__ == '__main__':
	unittest.main()
