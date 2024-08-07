# -*- coding: utf-8 -*-

import yaml
import sys

from snes2asm.decoder import *

class Configurator:
	def __init__(self, file_path):
		fp = open(file_path, 'r')
		self.config = yaml.safe_load(fp)
		fp.close()
		self.decoders_enabled = {'data': Decoder, 'array': ArrayDecoder, 'text': TextDecoder, 'gfx': GraphicDecoder, 'palette': PaletteDecoder, 'bin': BinaryDecoder, 'translation': TranslationMap, 'index': IndexDecoder, 'tilemap': TileMapDecoder, 'sound': SoundDecoder}
		self._validate()
		self.label_lookup = {}

	def _validate(self):
		if 'memory' in self.config:
			memory = self.config['memory']
			for variable in memory.keys():
				addr = memory[variable]
				if addr > 0x2000 and addr < 0x7E0000:
					memory.pop(variable)
					print("Warning: Ignoring out of range memory entry '%s' at address 0x%X" % (variable, addr))
					

	def apply(self, disasm):

		if 'banks' in self.config:
			banks = self.config['banks']
			if type(banks) == list:
				disasm.code_banks = banks

		if 'structs' in self.config:
			pass

		if 'decoders' in self.config:
			for decode_conf in self.config['decoders']:
				if decode_conf['type'] not in self.decoders_enabled:
					print("Unknown decoder type %s. Skipping." % decode_conf['type'])
					continue
				if 'compress' in decode_conf and decode_conf['compress'] not in compression.get_names():
					print("Unknown decoder compression %s. Skipping." % decode_conf['compress'])
					continue
				self.apply_decoder(disasm, decode_conf)

		if 'labels' in self.config:
			for label, index in self.config['labels'].items():
				disasm.label_name(index, label)

		if 'memory' in self.config:
			for variable, index in self.config['memory'].items():
				disasm.set_memory(index, variable)

	def apply_decoder(self, disasm, decode_conf):

		decoder_class = self.decoders_enabled[decode_conf['type']]
		if 'type' not in decode_conf:
			raise ValueError("Decoder missing type")
		del(decode_conf['type'])

		if 'label' not in decode_conf:
			raise ValueError("Decoder missing label")
		label = decode_conf['label']

		if label in self.label_lookup:
			raise ValueError("Duplicate label %s" % label)

		# Check if decoder transgresses bank boundry
		if 'start' in decode_conf and 'end' in decode_conf:
			dec_start = decode_conf.get('start')
			dec_end = decode_conf.get('end')
			if type(dec_start) != int:
				raise ValueError("Decoder %s invalid start position %s" % (label, str(dec_start)))
			if type(dec_end) != int:
				raise ValueError("Decoder %s invalid end position %s" % (label, str(dec_end)))
			if dec_start > dec_end:
				raise ValueError("Decoder %s invalid start and end positions" % label)
			bank_size = disasm.cart.bank_size()
			if dec_start // bank_size != (dec_end-1) // bank_size:
				raise ValueError("Decoder %s crosses bank boundry at positions 0x%x to 0x%x" % (label, dec_start, dec_end))

		# Replace decoder parameter references with actual object instances or sub decoder
		# {palette: 'sprites1_pal'} => {'palette: <PaletteDecoder instance at 0x1028e4fa0>}
		# {palette: {'param': 'value'} } => {'palette: <PaletteDecoder instance at 0x1028e4fa0>}
		for key, value in decode_conf.items():
			# If the property of a decoder matches the name of a decoder class
			if key in self.decoders_enabled.keys():
				# Is a label reference to another decoder
				if type(value) == str and value in self.label_lookup:
					decode_conf[key] = self.label_lookup[value]
				# Is a list of references
				elif type(value) == list:
					for i in range(0, len(value)):
						item = value[i]
						if type(item) == str and item in self.label_lookup:
							value[i] = self.label_lookup[item]
						else:
							raise ValueError("Could not find decoder label reference \"%s\" for decoder \"%s\"" % (item, str(decode_conf)))
				# Is a nested decoder with parameters
				elif type(value) == dict:
					value['type'] = key
					value['label'] = "%s_%s" % (label, key)
					decode_conf[key] = self.apply_decoder(disasm, value)
				else:
					raise ValueError("Could not find decoder label reference \"%s\" for decoder \"%s\"" % (value, str(decode_conf)))
		try:
			decoder_inst = decoder_class(**decode_conf)
		except TypeError as error:
			print("Error: Missing a required parameter from label: %s" % str(label))
			print(error)
			sys.exit()

		try:
			disasm.add_decoder(decoder_inst)
			self.label_lookup[label] = decoder_inst

		except ValueError as error:
			print("Could not add decoder type: %s" % str(error))

		return decoder_inst

class DataStruct:
	def __init__(self, name, props):
		self.name = name
		self.props = props
