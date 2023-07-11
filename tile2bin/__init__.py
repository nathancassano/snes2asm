# -*- coding: utf-8 -*-

import os
import sys
import argparse

from PyQt5.QtWidgets import QApplication
from tile2bin.application import App
from tile2bin.widget import Window

def main(argv=None):
	parser = argparse.ArgumentParser( prog="tile2bin", description='Tilemap editor', epilog='')
	parser.add_argument('input', metavar='map.tilemap', help="input tilemap file")

	args = parser.parse_args(argv[1:])

	if args.input:
		run(args)
	else:
		parser.print_help()

def run(options):
	qapp = QApplication(sys.argv)
	app = App(options)
	window = Window(app)
	window.show()
	sys.exit(qapp.exec_())
