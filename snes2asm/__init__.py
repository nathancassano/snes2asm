# -*- coding: utf-8 -*-

import os
import sys
import re
import logging
import argparse

from snes2asm.disassembler import Disassembler
from snes2asm.cartridge import Cartridge
from snes2asm.project_maker import ProjectMaker
from snes2asm.configurator import Configurator
from snes2asm.decoder import Headers

def main(argv=None):
	parser = argparse.ArgumentParser( prog="snes2asm", description='Disassembles snes cartridges into practical projects', epilog='')
	parser.add_argument('input', metavar='snes.sfc', help="input snes file")
	parser.add_argument('-v', '--verbose', action='store_true', default=None, help="Verbose output")
	parser.add_argument('-o', '--output_dir', default='.', help="File path to output project")
	parser.add_argument('-c', '--config', default=None, help="Path to decoding configuration yaml file")
	parser.add_argument('-b', '--banks', nargs='+', type=int, help='Code banks to disassemble. Default is auto-detect')
	parser.add_argument('-hi', '--hirom', action='store_true', default=None, help="Force HiROM")
	parser.add_argument('-lo', '--lorom', action='store_true', default=None, help="Force LoROM")
	parser.add_argument('-f', '--fastrom', action='store_true', default=None, help="Force fast ROM addressing")
	parser.add_argument('-s', '--slowrom', action='store_true', default=None, help="Force slow ROM addressing")
	parser.add_argument('-nl', '--nolabel', action='store_true', default=None, help="Use addresses instead of labels")
	parser.add_argument('-x', '--hex', action='store_true', default=None, help="Comments show instruction hex")

	args = parser.parse_args(argv[1:])

	if args.input:
		exec_asm(args)
	else:
		parser.print_help()

def exec_asm(options):
	cart = Cartridge(options.__dict__)
	cart.open(options.input)

	disasm = Disassembler(cart, options)
	disasm.add_decoder(Headers(cart.header,cart.header+80))

	if options.config:
		configurator = Configurator(options.config)
		configurator.apply(disasm)

	disasm.run()

	project = ProjectMaker(cart, disasm)
	project.output(options.output_dir)

def bmp2chr(argv=None):
	parser = argparse.ArgumentParser( prog="bmp2chr", description='Convert indexed bitmap to CHR data', epilog='')
	parser.add_argument('input', metavar='input.bmp', help="input bitmap file")

	args = parser.parse_args(argv[1:])

	if args.input:
		print "TODO"
	else:
		parser.print_help()

