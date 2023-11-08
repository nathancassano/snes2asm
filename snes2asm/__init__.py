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
from snes2asm.tile import *
from snes2asm.bitmap import BitmapIndex
from snes2asm import compression


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

	if options.banks:
		disasm.code_banks = options.banks

	if options.config:
		configurator = Configurator(options.config)
		try:
			configurator.apply(disasm)
		except ValueError as e:
			print("Error: %s" % str(e))
			sys.exit(-1)

	disasm.run()

	project = ProjectMaker(cart, disasm)
	project.output(options.output_dir)

def bmp2chr(argv=None):
	parser = argparse.ArgumentParser( prog="bmp2chr", description='Convert an indexed bitmap to SNES CHR data', epilog='')
	parser.add_argument('input', metavar='input.bmp', help="input bitmap file")
	parser.add_argument('-o', '--output', required=True, default=None, help="File path to output *.chr")
	parser.add_argument('-b2', '--b2pp', action='store_true', default=False, help="4 colors planar graphic output")
	parser.add_argument('-b3', '--b3pp', action='store_true', default=False, help="8 colors planar graphic output")
	parser.add_argument('-b4', '--b4pp', action='store_true', default=True, help="16 colors planar graphic output")
	parser.add_argument('-b8', '--b8pp', action='store_true', default=False, help="256 colors planar graphic output")
	parser.add_argument('-l2', '--linear2', action='store_true', default=False, help="4 colors linear graphic output")
	parser.add_argument('-l4', '--linear4', action='store_true', default=True, help="16 colors linear graphic output")
	parser.add_argument('-l8', '--linear8', action='store_true', default=False, help="256 colors linear graphic output")
	parser.add_argument('-p', '--palette', action='store_true', default=False, help="Output color *.pal file")
	parser.add_argument('-f', '--fullsize', action='store_true', default=False, help="Ignore destination CHR file size and write whole bitmap")
	args = parser.parse_args(argv[1:])

	if args.input:
		try:
			b = BitmapIndex.read(args.input)
		except Exception as e:
			print("Error: %s" % str(e))
			return -1

		if args.b2pp:
			encode = Encode2bppTile
			depth = 2
		elif args.b8pp:
			encode = Encode8bppTile
			depth = 8
		elif args.l8:
			encode = EncodeLinear8Tile
			depth = 8
		elif args.l4:
			encode = EncodeLinear4Tile
			depth = 4
		elif args.l2:
			encode = EncodeLinear2Tile
			depth = 2
		elif args.b3pp:
			encode = Encode3bppTile
			depth = 3
		else:
			encode = Encode4bppTile
			depth = 4

		if depth != b._bcBitCount:
			print("Error: Bitmap file %s does not have a bit depth of %d" % (args.input, depth))
			return -1

		if b._bcWidth % 8 != 0 or b._bcHeight % 8 != 0:
			print("Error: Bitmap file %s does not have multiple tile dimensions of 8x8" % args.input)
			return -1

		# For odd shaped bitmaps match the number of tiles in the destination chr file by limiting the size
		if os.path.isfile(args.output) and not args.maxsize:
			max_size = os.path.getsize(args.output)
		else:
			max_size = b._bcBitCount * b._bcWidth * b._bcHeight

		try:
			chr_fp = open(args.output, "wb")
		except Exception as e:
			print("Error: %s" % str(e))
			return -1

		# Write tile data
		running = True
		for ty in range(0, b._bcHeight, 8):
			for tx in range(0, b._bcWidth, 8):
				tile = bytearray()
				for y in range(ty, ty+8):
					for x in range(tx, tx+8):
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

def get_compression_module_names():
	from inspect import getmembers, ismodule
	return [m[0] for m in getmembers(compression, ismodule)]

def packer(argv=None):
	parser = argparse.ArgumentParser( prog="packer", description='Encode and decode files with compression', epilog='')
	parser.add_argument('action', metavar='pack|unpack', help="Action type")
	parser.add_argument('input', metavar='input.bin', help="Input file")
	parser.add_argument('-o', '--output', required=True, metavar='outfile', default=None, help="File path to output")
	parser.add_argument('-x', '--encoding', metavar='|'.join(get_compression_module_names()), required=True, type=str, help='Encoding algorithm')
	parser.add_argument('-f', '--fullsize', action='store_true', default=False, help="Ignore destination file size and write full data")

	args = parser.parse_args(argv[1:])

	if not args.action or args.action not in ['pack', 'unpack']:
		parser.print_help()
		return 0

	if args.input:
		try:
			in_fp = open(args.input, "rb")
			data = in_fp.read()
			in_fp.close()
		except Exception as e:
			print("Error: %s" % str(e))
			return -1
		
		try:
			module = getattr(compression, args.encoding)
		except AttributeError:
			print("Unsupported encoding type: %s. Use following types %s." % (args.encoding, ",".join(get_compression_module_names())))
			return -1

		if args.action == 'pack':
			output = module.compress(data)
		else:
			output = module.decompress(data)

		# If target file already exists then regulate output size
		if os.path.isfile(args.output):
			size = os.path.getsize(args.output)
			if not args.fullsize and size > 0:
				if size > len(output):
					output = output + bytes(size - len(output))
				elif size < len(output):
					print("Warning: Truncating output of compression for file %s" % args.output)
					output = output[0:size]
		try:
			out_fp = open(args.output, "wb")
			out_fp.write(output)
			out_fp.close()
		except Exception as e:
			print("Error: %s" % str(e))
			return -1
	else:
		parser.print_help()
	return 0
