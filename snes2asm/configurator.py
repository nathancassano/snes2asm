# -*- coding: utf-8 -*-

import yaml
import sys

from snes2asm.decoder import *

class Configurator:
	def __init__(self, file_path):
		fp = open(file_path, 'r')
		self.config = yaml.safe_load(fp)
		fp.close()
		self.decoders_enabled = {'data': Decoder, 'array': ArrayDecoder, 'text': TextDecoder, 'gfx': GraphicDecoder, 'palette': PaletteDecoder, 'bin': BinaryDecoder, 'translation': TranslationMap, 'index': IndexDecoder, 'tilemap': TileMapDecoder, 'sound': SoundDecoder, 'spc700': SPC700Decoder}
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

	def build_decoder(self, disasm, decode_conf, add_to_disasm=True):
		"""
		Build a decoder instance from configuration.

		Args:
			disasm: The disassembler instance
			decode_conf: Decoder configuration dict
			add_to_disasm: If True, add decoder to disassembler (default).
			               If False, only create the decoder instance.

		Returns:
			The decoder instance
		"""
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
		# {decoders: [{'type': 'sound', ...}, ...]} => {'decoders': [<SoundDecoder instance>, ...]}
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
					decode_conf[key] = self.build_decoder(disasm, value)
				else:
					raise ValueError("Could not find decoder label reference \"%s\" for decoder \"%s\"" % (value, str(decode_conf)))

		# Special handling for 'decoders' key. A list of inline decoder definitions. Yo dog I heard you like decoders inside of your decoders.
		if 'decoders' in decode_conf:
			decoders_list = decode_conf['decoders']
			if type(decoders_list) == list:
				processed_decoders = []
				for i, item in enumerate(decoders_list):
					# Handle inline decoder definition (dict)
					if type(item) == dict:
						# Ensure it has a type
						if 'type' not in item:
							raise ValueError("Decoder in decoders list for '%s' missing 'type' field" % label)
						# Generate a label if not provided
						if 'label' not in item:
							item['label'] = "%s_decoder_%d" % (label, i)
						# Build the decoder but DON'T add it to disassembler
						# (it will be processed by the parent decoder)
						processed_decoders.append(self.build_decoder(disasm, item, add_to_disasm=False))
					# Handle string reference to existing decoder
					elif type(item) == str:
						if item in self.label_lookup:
							processed_decoders.append(self.label_lookup[item])
						else:
							raise ValueError("Could not find decoder label reference \"%s\" in decoders list for \"%s\"" % (item, label))
					else:
						raise ValueError("Invalid item in decoders list for '%s': must be dict or string reference" % label)
				decode_conf['decoders'] = processed_decoders

		# Add hex_comment flag for SPC700Decoder
		if decoder_class.__name__ == 'SPC700Decoder':
			decode_conf['hex_comment'] = disasm.hex_comment

		try:
			decoder_inst = decoder_class(**decode_conf)
		except TypeError as error:
			print("Error: Missing a required parameter from label: %s" % str(label))
			print(error)
			sys.exit()

		# Only add to disassembler if requested (nested decoders are not added)
		if add_to_disasm:
			try:
				disasm.add_decoder(decoder_inst)
				self.label_lookup[label] = decoder_inst
			except ValueError as error:
				print("Could not add decoder type: %s" % str(error))

		return decoder_inst

	def apply_decoder(self, disasm, decode_conf):
		"""Wrapper for build_decoder that always adds to disassembler"""
		return self.build_decoder(disasm, decode_conf, add_to_disasm=True)

class DataStruct:
	def __init__(self, name, props):
		self.name = name
		self.props = props
