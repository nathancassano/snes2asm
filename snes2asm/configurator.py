
from snes2asm.disassembler import Decoder, TextDecoder

import yaml

class Configurator:
	def __init__(self, file_path):
		self.config = yaml.safe_load(file(file_path, 'r'))
		self.decoders_enabled = {'data': Decoder, 'ascii': TextDecoder}
		self._validate()

	def _validate(self):
		pass

	def apply(self, disasm):

		if self.config.has_key('structs'):
			pass

		if self.config.has_key('decoders'):
			for decode_conf in self.config['decoders']:
				if decode_conf['type'] in self.decoders_enabled:
					decoder_class = self.decoders_enabled[decode_conf['type']]
					del(decode_conf['type'])
					decoder_inst = decoder_class(**decode_conf)
					disasm.add_decoder(decoder_inst)
				else:
					print "Unknown decoder type %s. Skipping." % decode_conf['type']

		if self.config.has_key('labels'):
			for label, index in self.config['labels'].items():
				disasm.set_label(index, label)

class DataStruct:
	def __init__(self, name, props):
		self.name = name
		self.props = props
