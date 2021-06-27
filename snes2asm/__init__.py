# -*- coding: utf-8 -*-

import os
import sys
import re
import logging
import argparse

from snes2asm.disassembler import Disassembler
from snes2asm.cartridge import Cartridge

def main(argv=None):
	parser = argparse.ArgumentParser( prog="snes2asm", description='Disassembles snes cartridges into practical projects', epilog='')
	parser.add_argument('input', metavar='snes.sfc', help="input snes file")
	parser.add_argument('-b', '--banks', nargs='+', type=int, help='Code banks to disassemble. Default is auto-detect')
	parser.add_argument('-v', '--verbose', action='store_true', default=None, help="verbose output")
	parser.add_argument('-hi', '--hirom', action='store_true', default=None, help="Force HiROM")
	parser.add_argument('-lo', '--lorom', action='store_true', default=None, help="Force LoROM")
	parser.add_argument('-s', '--shadow', action='store_true', default=None, help="Force shadow ROM")
	parser.add_argument('-ns', '--noshadow', action='store_true', default=None, help="No ROM shadow")

	args = parser.parse_args(argv[1:])

	if args.input:
		exec_asm(args)
	else:
		parser.print_help()

def exec_asm(args):

	cart = Cartridge(args)
	cart.open(args.input)

	disasm = Disassembler(cart)
	disasm.run()
	disasm.output('.')
