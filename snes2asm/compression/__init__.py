# -*- coding: utf-8 -*-

from snes2asm.compression import aplib
from snes2asm.compression import byte_rle
from snes2asm.compression import rle1
from snes2asm.compression import rle2
from snes2asm.compression import lz1
from snes2asm.compression import lz2
from snes2asm.compression import lz3
from snes2asm.compression import lz4
from snes2asm.compression import lz5
from snes2asm.compression import lz19
from snes2asm.compression import hal

def get_names():
	import sys
	from inspect import getmembers, ismodule
	return [m[0] for m in getmembers(sys.modules[__name__], ismodule)]

def get_encoding(encoding):
	import sys
	return getattr(sys.modules[__name__], encoding)

def compress(encoding, data):
	return get_encoding(encoding).compress(data)

def decompress(encoding, data):
	return get_encoding(encoding).decompress(data)

