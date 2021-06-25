# -*- coding: utf-8 -*-

import os
import sys
import re
import logging
import argparse

from snes2asm.disassembler import Disassembler
from snes2asm.cartridge import Cartridge

def main(argv=None):
	parser = argparse.ArgumentParser(
		prog="snes2asm",
		description='Disassembles snes cartridges into practical projects',
		epilog='')

	parser.add_argument('-v', '--verbose', action='store_true', help="verbose output")

	args = parser.parse_args(argv[1:])
	exec_asm(args)

def exec_asm(args)
    cart = Cartridge(args[0])
    cart.open(snes_file)

    disasm = Disassembler(cart)
	disasm.output('.')
