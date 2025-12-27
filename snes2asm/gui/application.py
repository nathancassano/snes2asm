# -*- coding: utf-8 -*-

import os
import sys
import yaml

class Document:

	def __init__(self):
		self.changed = True

	def loadYaml(self, filename):
		meta_format = yaml.load(filename)

		# Format validation and assignment
		for prop, value in meta_format.items():
			pass

	def title(self):
		return ""

	def filepath(self):
		return os.path.join(self.working_dir, self.filename)

class App:
	def __init__(self, args):
		self.docs = []

	def addDoc(self, doc):
		self.docs.append(doc)

	def removeDoc(self, index):
		self.docs.remove(self.docs[index])

