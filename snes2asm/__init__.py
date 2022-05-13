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
from snes2asm.tile import Encode8bppTile, Encode4bppTile, Encode2bppTile
from snes2asm.bitmap import BitmapIndex

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
	parser = argparse.ArgumentParser( prog="bmp2chr", description='Convert an indexed bitmap to SNES CHR data', epilog='')
	parser.add_argument('input', metavar='input.bmp', help="input bitmap file")
	parser.add_argument('-o', '--output', required=True, default=None, help="File path to output *.chr")
	parser.add_argument('-b2', '--b2pp', action='store_true', default=False, help="4 colors graphic output")
	parser.add_argument('-b4', '--b4pp', action='store_true', default=True, help="16 colors graphic output")
	parser.add_argument('-b8', '--b8pp', action='store_true', default=False, help="256 colors graphic output")
	parser.add_argument('-p', '--palette', action='store_true', default=False, help="Output color *.pal file")
	parser.add_argument('-m', '--maxsize', action='store_true', default=False, help="Ignore destination CHR file size and write whole bitmap")
	args = parser.parse_args(argv[1:])

	if args.input:
		try:
			b = BitmapIndex.read(args.input)
		except Exception as e:
			print "Error: %s" % str(e)
			return -1

		if args.b2pp:
			encode = Encode2bppTile
			depth = 2
		elif args.b8pp:
			encode = Encode8bppTile
			depth = 8
		else:
			encode = Encode4bppTile
			depth = 4

		if depth != b._bcBitCount:
			print "Error: Bitmap file %s does not have a bit depth of %d" % (args.input, depth)
			return -1

		if b._bcWidth % 8 != 0 or b._bcHeight % 8 != 0:
			print "Error: Bitmap file %s does not have multiple tile dimensions of 8x8" % args.input
			return -1

		# For odd shaped bitmaps match the number of tiles in the destination chr file by limiting the size
		if os.path.isfile(args.output) and not args.maxsize:
			max_size = os.path.getsize(args.output)
		else:
			max_size = b._bcBitCount * b._bcWidth * b._bcHeight

		try:
			chr_fp = open(args.output, "wb")
		except Exception as e:
			print "Error: %s" % str(e)
			return -1

		# Write tile data
		running = True
		for ty in xrange(0, b._bcHeight, 8):
			for tx in xrange(0, b._bcWidth, 8):
				tile = bytearray()
				for y in xrange(ty, ty+8):
					for x in xrange(tx, tx+8):
						tile.append(b.getPixel(x, y))
				chr_fp.write(encode(tile))
				if chr_fp.tell() >= max_size:
					running = False
					break

			if not running:
				break
		chr_fp.close()
	else:
		parser.print_help()
	return 0

