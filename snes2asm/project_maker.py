import os

class ProjectMaker:

	def __init__(self, disasm):
		self.disasm = disasm

	def output(self, dir, name):
		for i in range(0,len(self.disasm.banks)):
			filename = "%s/bank%d.asm" % (dir, i)
			f = open(filename, 'w')
			f.write( str(self.disasm.banks[i]))
			f.close()
