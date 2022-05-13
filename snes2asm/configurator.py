# -*- coding: utf-8 -*-

import yaml

from snes2asm.decoder import *

class Configurator:
	def __init__(self, file_path):
		self.config = yaml.safe_load(file(file_path, 'r'))
		self.decoders_enabled = {'data': Decoder, 'ascii': TextDecoder, 'gfx': GraphicDecoder, 'palette': PaletteDecoder}
		self._validate()

	def _validate(self):
		pass

	def apply(self, disasm):

		if self.config.has_key('banks'):
			banks = self.config['banks']
			if type(banks) == list:
				disasm.options.banks = banks

		if self.config.has_key('structs'):
			pass

		if self.config.has_key('decoders'):
			label_lookup = {}
			for decode_conf in self.config['decoders']:
				if decode_conf['type'] not in self.decoders_enabled:
					print "Unknown decoder type %s. Skipping." % decode_conf['type']
					continue

				decoder_class = self.decoders_enabled[decode_conf['type']]
				if 'type' not in decode_conf:
					raise ValueError("Decoder missing type")
				del(decode_conf['type'])

				if 'label' not in decode_conf:
					raise ValueError("Decoder missing label")
				label = decode_conf['label']

				# Replace decoder parameter references with actual object instances
				# {palette: 'sprites1_pal'} => {'palette: <PaletteDecoder instance at 0x1028e4fa0>}
				for key, value in decode_conf.items():
					if key in self.decoders_enabled.keys():
						if label_lookup.has_key(value):
							decode_conf[key] = label_lookup[value]
						else:
							raise ValueError("Could not find decoder label reference \"%s\" for decoder \"%s\"" % (value, str(decode_conf)))

				decoder_inst = decoder_class(**decode_conf)
				try:
					disasm.add_decoder(decoder_inst)
					label_lookup[label] = decoder_inst

				except ValueError as error:
					print "Could not add decoder type: %s" % str(error)

		if self.config.has_key('labels'):
			for label, index in self.config['labels'].items():
				disasm.label_name(index, label)

		if self.config.has_key('memory'):
			for variable, index in self.config['memory'].items():
				disasm.set_memory(index, variable)

class DataStruct:
	def __init__(self, name, props):
		self.name = name
		self.props = props
