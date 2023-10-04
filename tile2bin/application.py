# -*- coding: utf-8 -*-

import os
import sys
import argparse
import struct
import yaml

class TileMapEntry:
	def __init__(self, pack):
		self.tile_index = pack & 0x3F
		self.palette_index = (pack & 0x1C00) >> 10
		self.vertical_flip = (pack & 0x8000) != 0
		self.horizontal_flip = (pack & 0x4000) != 0
		self.priority = (pack & 0x2000) != 0

	def pack(self):
		pack = self.tile_index & 0x3F
		pack = pack | (self.palette_index & 0x7 ) << 10
		pack = pack | 0x8000 if self.vertical_flip else 0
		pack = pack | 0x4000 if self.horizontal_flip else 0
		pack = pack | 0x2000 if self.priority else 0
		return struct.pack('<H', pack)

class TileMapMode7Entry:
	def __init__(self, index):
		self.tile_index = index

	def pack(self):
		return struct.pack('B', self.tile_index)

class TileDocument:

	def __init__(self):
		self.tile_map_entry = []
		self.palette_entry = []
		self.filename = 'Untitled'
		self.working_dir = os.getcwd()

		self.width = 64
		self.height = 64
		self.tilechr = 'Untitled.chr'
		self.gfx = ''
		self.tilesize = 8
		self.palette = 'Untitled.pal'
		self.palette_offset = 0
		self.mode7 = False
		self.changed = True

	def pixWidth(self):
		return self.width * self.tilesize

	def pixHeight(self):
		return self.height * self.tilesize
		
	def loadYaml(self, filename):
		meta_format = yaml.load(filename)

		# Format validation and assignment
		for prop, value in meta_format.items():
			if hasattr(self, prop):
				if type(getattr(self, prop)) != type(value):
					raise ValueError("Invalid value type for file '%s' for property named '%s'" % (filename, prop))
				setattr(self, prop, value);
			else:
				print("Ignoring file property named '%s'", prop)

		self.working_dir = os.path.dirname(os.path.realpath(filename))
		self.filename = os.path.basename(filename)

	def title(self):
		return self.filename.replace('.tilemap', '')

	def filepath(self):
		return os.path.join(self.working_dir, self.filename)

	def _chrFileName(self):
		return os.path.join(self.working_dir, self.tilechr)

	def _palFileName(self):
		return os.path.join(self.working_dir, self.palette)

	def loadChr(self):

		f = open(self._chrFileName(), 'rb')
		data = f.read()
		f.close()

		if self.mode7:
			self.loadChrMode7Data(data)
		else:
			self.loadChrData(data)

	def loadChrData(self, data):

		if len(data) != (self.width * self.height * 2):
			raise Exception("Invalid size of chr file %s(%d) for dimensions w=%d h=%d" % (chr_filename, len(data), self.width, self.height))

		self.tile_map_entry = []
		index = 0
		for y in range(0, self.height):
			row = []
			for x in range(0, self.width):
				pack = data[index] | data[index+1] << 8
				row.append( TileMapEntry( pack ) )
				index = index + 2
			self.tile_map_entry.append(row)

	def loadChrMode7Data(self, data):

		if len(data) != (self.width * self.height):
			raise Exception("Invalid size of chr file %s(%d) for dimensions w=%d h=%d" % (chr_filename, len(data), self.width, self.height))

		self.tile_map_entry = []
		index = 0
		for y in range(0, self.height):
			row = []
			for x in range(0, self.width):
				row.append( TileMapMode7Entry( data[index] ) )
				index = index + 1
			self.tile_map_entry.append(row)

	def saveChr(self):
		f = open(self._chrFileName(), 'wb')
		for y in range(0, self.height):
			for x in range(0, self.width):
				f.write( self.tile_map_entry[y][x].pack() )
		f.close()

	def loadPalette(self):
		f = open(self._palFileName(), 'rb')
		data = f.read()
		f.close()

		self.palette_entry= []
		for index in range(0, len(data), 2):
			bgr565 = data[index] | data[index+1] << 8
			rgbcolor = (bgr565 & 0x7c00) >> 7 | (bgr565 & 0x3e0) << 6 | (bgr565 & 0x1f) << 19
			self.palette_entry.append(rgbcolor)

	def savePalette(self):
		f = open(self._palFileName(), 'wb')

		for index in range(0, len(self.palette_entry)):
			rgbcolor = self.palette_entry[index]
			bgr565 = (rgbcolor << 7) & 0x7c00 | (rgbcolor >> 6) & 0x3e0 | (rgbcolor >> 19) & 0x1f
			f.write(struct.pack('<h', bgr565))
		f.close()

	def save(self):
		self.savePalette()
		self.saveChr()

class App:
	def __init__(self, args):
		self.docs = []

	def addDoc(self, doc):
		self.docs.append(doc)

	def removeDoc(self, index):
		self.docs.remove(self.docs[index])

