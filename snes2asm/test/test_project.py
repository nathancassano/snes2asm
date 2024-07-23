# -*- coding: utf-8 -*-

import unittest
import os
import shutil
from snes2asm import main

class ProjectTest(unittest.TestCase):
	
	def test_run(self):
		cwd = os.getcwd()
		directory = os.path.dirname(__file__)
		path = os.path.join(directory, 'classickong.smc')
		conf = os.path.join(directory, 'classickong.yaml')
		out = os.path.join(directory, 'project')
		game = os.path.join(out, 'game.smc')

		# ./snes2asm -o project -e 0 -c classickong.yaml classickong.smc
		main(['snes2asm', '-o', out, '-e', 0,  '-c', conf, path])

		# Run make to compile ROM
		os.chdir(out)
		self.assertEqual(0, os.system('make'))
		os.chdir(cwd)

		# Compare binary files
		with open(path, "r") as f:
			expected_lines = self.hexdump(f.read())
		with open(game, "r") as f:
			actual_lines = self.hexdump(f.read())

		self.assertListEqual(expected_lines, actual_lines)
	
		# Clean up
		shutil.rmtree(out)

	def hexdump(self, data):
		out = []
		for h in range(0, len(data), 16):
			out.append(('%06X ' % h) + ' '.join(['%02x' % ord(c) for c in data[h:h+16]]))
		return out

if __name__ == '__main__':
	unittest.main()
