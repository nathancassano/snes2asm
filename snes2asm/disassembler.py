import snes2asm
from collections import OrderedDict
import bisect

from snes2asm.cartridge import Cartridge
from snes2asm.rangetree import RangeTree

InstructionSizes = [
	2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 1, 1, 3, 3, 3, 4, # x0
	2, 2, 2, 2, 2, 2, 2, 2, 1, 3, 1, 1, 3, 3, 3, 4, # x1
	3, 2, 4, 2, 2, 2, 2, 2, 1, 2, 1, 1, 3, 3, 3, 4, # x2
	2, 2, 2, 2, 2, 2, 2, 2, 1, 3, 1, 1, 3, 3, 3, 4, # x3
	1, 2, 2, 2, 3, 2, 2, 2, 1, 2, 1, 1, 3, 3, 3, 4, # x4
	2, 2, 2, 2, 3, 2, 2, 2, 1, 3, 1, 1, 4, 3, 3, 4, # x5
	1, 2, 3, 2, 2, 2, 2, 2, 1, 2, 1, 1, 3, 3, 3, 4, # x6
	2, 2, 2, 2, 2, 2, 2, 2, 1, 3, 1, 1, 3, 3, 3, 4, # x7
	2, 2, 3, 2, 2, 2, 2, 2, 1, 2, 1, 1, 3, 3, 3, 4, # x8
	2, 2, 2, 2, 2, 2, 2, 2, 1, 3, 1, 1, 3, 3, 3, 4, # x9
	2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 1, 1, 3, 3, 3, 4, # xA
	2, 2, 2, 2, 2, 2, 2, 2, 1, 3, 1, 1, 3, 3, 3, 4, # xB
	2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 1, 1, 3, 3, 3, 4, # xC
	2, 2, 2, 2, 2, 2, 2, 2, 1, 3, 1, 1, 3, 3, 3, 4, # xD
	2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 1, 1, 3, 3, 3, 4, # xE
	2, 2, 2, 2, 3, 2, 2, 2, 1, 3, 1, 1, 3, 3, 3, 4, # xF 
]

# Static Regions of memory 
# Format: Address: ["Symbol", "Comment"]
StaticAddresses = {
	0x2100: ["INIDSP", "Screen Display"],
	0x2101: ["OBJSEL", "Object Size and Chr Address"],
	0x2102: ["OAMADDL", "OAM Address Low Byte"],
	0x2103: ["OAMADDH", "OAM Address High Byte"],
	0x2104: ["OAMDATA", "Data for OAM write"],
	0x2105: ["BGMODE", "BG Mode and Character Size"],
	0x2106: ["MOSAIC", "Screen Pixelation"],
	0x2107: ["BG1SC", "BG1 Tilemap Address and Size"],
	0x2108: ["BG2SC", "BG2 Tilemap Address and Size"],
	0x2109: ["BG3SC", "BG3 Tilemap Address and Size"],
	0x210a: ["BG4SC", "BG4 Tilemap Address and Size"],
	0x210b: ["BG12NBA", "BG1&2 Tilemap Character Address"],
	0x210c: ["BG34NBA", "BG3&4 Tilemap Character Address"],
	0x210d: ["BG1HOFS", "BG1 Horizontal Scroll / Mode 7 BG Horizontal Scroll"],
	0x210e: ["BG1VOFS", "BG1 Vertical Scroll / Mode 7 BG Vertical Scroll"],
	0x210f: ["BG2HOFS", "BG2 Horizontal Scroll"],
	0x2110: ["BG2VOFS", "BG2 Vertical Scroll"],
	0x2111: ["BG3HOFS", "BG3 Horizontal Scroll"],
	0x2112: ["BG3VOFS", "BG3 Vertical Scroll"],
	0x2113: ["BG4HOFS", "BG4 Horizontal Scroll"],
	0x2114: ["BG4VOFS", "BG4 Vertical Scroll"],
	0x2115: ["VMAIN", "Video Port Control"],
	0x2116: ["VMADDL", "VRAM Address Low Byte"],
	0x2117: ["VMADDH", "VRAM Address High Byte"],
	0x2118: ["VMDATAL", "VRAM Data Write Low Byte"],
	0x2119: ["VMDATAH", "VRAM Data Write High Byte"],
	0x211a: ["M7SEL", "Mode 7 Settings"],
	0x211b: ["M7A", "Mode 7 Matrix A"],
	0x211c: ["M7B", "Mode 7 Matrix B"],
	0x211d: ["M7C", "Mode 7 Matrix C"],
	0x211e: ["M7D", "Mode 7 Matrix D"],
	0x211f: ["M7X", "Mode 7 Center X"],
	0x2120: ["M7Y", "Mode 7 Center Y"],
	0x2121: ["CGADD", "CGRAM Address"],
	0x2122: ["CGDATA", "CGRAM Data Write"],
	0x2123: ["W12SEL", "Window Mask Settings for BG1 and BG2"],
	0x2124: ["W34SEL", "Window Mask Settings for BG3 and BG4"],
	0x2125: ["WOBJSEL", "Window Mask Settings for Objects and Color Window"],
	0x2126: ["W1L", "Window 1 Left Position"],
	0x2127: ["W1R", "Window 1 Right Position"],
	0x2128: ["W2L", "Window 2 Left Position"],
	0x2129: ["W2R", "Window 2 Right Position"],
	0x212a: ["WBGLOG", "Window Mask Logic for Backgrounds"],
	0x212b: ["WOBJLOG", "Window Mask Logic for Objects and Color Window"],
	0x212c: ["TMAIN", "Mainscreen Designation"],
	0x212d: ["TSUB", "Subscreen Designation"],
	0x212e: ["TMW", "Window Mask Designation for the Main Screen"],
	0x212f: ["TSW", "Window Mask Designation for the Subscreen"],
	0x2130: ["CGWSEL", "Color Addition Select"],
	0x2131: ["CGADSUB", "Color Math Designation"],
	0x2132: ["COLDATA", "Fixed Color Data"],
	0x2133: ["SETINI", "Screen Mode/Video Select"],
	0x2134: ["MPYL", "Multiplication Result Low Byte"],
	0x2135: ["MPYM", "Multiplication Result Middle Byte"],
	0x2136: ["MPYH", "Multiplication Result High Byte"],
	0x2137: ["SLHV", "Software Latch for H/V Counter"],
	0x2138: ["OAMDATAREAD", "Data for OAM read"],
	0x2139: ["VMDATALREAD", "VRAM Data Read Low Byte"],
	0x213a: ["VMDATAHREAD", "VRAM Data Read High Byte"],
	0x213b: ["CGDATAREAD", "CGRAM Data Read"],
	0x213c: ["OPHCT", "Horizontal Scanline Location"],
	0x213d: ["OPVCT", "Vertical Scanline Location"],
	0x213e: ["STAT77", "5C77 PPU-1 Status Flag and Version"],
	0x213f: ["STAT78", "5C78 PPU-2 Status Flag and Version"],
	0x2140: ["APUIO0", "APU I/O Port 0"],
	0x2141: ["APUIO1", "APU I/O Port 1"],
	0x2142: ["APUIO2", "APU I/O Port 2"],
	0x2143: ["APUIO3", "APU I/O Port 4"],
	0x2180: ["WMDATA", "WRAM Data Read/Write"],
	0x2181: ["WMADDL", "WRAM Address Low Byte"],
	0x2182: ["WMADDM", "WRAM Address Middle Byte"],
	0x2183: ["WMADDH", "WRAM Address High Byte"],
	0x4016: ["JOYSER0", "Joypad Port 1"],
	0x4017: ["JOYSER1", "Joypad Port 2"],
	0x4200: ["NMITIMEN", "Interrupt Enable Flags"],
	0x4201: ["WRIO", "I/O port output/write"],
	0x4202: ["WRMPYA", "Multiplicand A"],
	0x4203: ["WRMPYB", "Multplier B"],
	0x4204: ["WRDIVL", "Dividend Low Byte"],
	0x4205: ["WRDIVH", "Dividend High Byte"],
	0x4206: ["WRDIVB", "Divisor"],
	0x4207: ["HTIMEL", "H-Count Timer"],
	0x4208: ["HTIMEH", "H-Count Timer MSB"],
	0x4209: ["VTIMEL", "V-Count Timer"],
	0x420a: ["VTIMEH", "V-Count Timer MSB"],
	0x420b: ["MDMAEN", "DMA Channel Enable"],
	0x420c: ["HDMAEN", "HDMA Channel Enable"],
	0x420d: ["MEMSEL", "ROM Access Speed"],
	0x4210: ["RDNMI", "NMI Flag and 5A22 Version"],
	0x4211: ["TIMEUP", "IRQ Flag"],
	0x4212: ["HVBJOY", "H/V Blank Flags and Joypad Status"],
	0x4213: ["RDIO", "I/O port input/read"],
	0x4214: ["RDDIVL", "Quotient of Divide Result Low Byte"],
	0x4215: ["RDDIVH", "Quotient of Divide Result High Byte"],
	0x4216: ["RDMPYL", "Multiplication Product or Divide Remainder Low Byte"],
	0x4217: ["RDMPYH", "Multiplication Product or Divide Remainder High Byte"],
	0x4218: ["JOY1L", "Joyport1 Data Low Byte"],
	0x4219: ["JOY1H", "Joyport1 Data High Byte"],
	0x421a: ["JOY2L", "Joyport2 Data Low Byte"],
	0x421b: ["JOY2H", "Joyport2 Data High Byte"],
	0x421c: ["JOY3L", "Joyport3 Data Low Byte"],
	0x421d: ["JOY3H", "Joyport3 Data High Byte"],
	0x421e: ["JOY4L", "Joyport4 Data Low Byte"],
	0x421f: ["JOY4H", "Joyport4 Data High Byte"],
	0x4300: ["DMAP0", "DMA 0 Control"],
	0x4301: ["DMADEST0", "DMA 0 Destination Register"],
	0x4302: ["DMASRC0L", "DMA 0 Source Adress Low Byte"],
	0x4303: ["DMASRC0H", "DMA 0 Source Address High Byte"],
	0x4304: ["DMASRC0B", "DMA 0 Source Address Bank"],
	0x4305: ["DMALEN0L", "DMA 0 Transfer Size Low Byte"],
	0x4306: ["DMALEN0H", "DMA 0 Transfer Size High Byte"],
	0x4307: ["DMALEN0B", "DMA 0 Transfer Bank"],
	0x4308: ["HDMATBL0L", "HDMA 0 Table Address Low Byte"],
	0x4309: ["HDMATBL0H", "HDMA 0 Table Address High Byte"],
	0x430a: ["HDMACNT0", "HDMA 0 Line Counter"],
	0x4310: ["DMAP1", "DMA 1 Control"],
	0x4311: ["DMADEST1", "DMA 1 Destination Register"],
	0x4312: ["DMASRC1L", "DMA 1 Source Adress Low Byte"],
	0x4313: ["DMASRC1H", "DMA 1 Source Address High Byte"],
	0x4314: ["DMASRC1B", "DMA 1 Source Address Bank"],
	0x4315: ["DMALEN1L", "DMA 1 Transfer Size Low Byte"],
	0x4316: ["DMALEN1H", "DMA 1 Transfer Size High Byte"],
	0x4317: ["DMALEN1B", "DMA 1 Transfer Bank"],
	0x4318: ["HDMATBL1L", "HDMA 1 Table Address Low Byte"],
	0x4319: ["HDMATBL1H", "HDMA 1 Table Address High Byte"],
	0x431a: ["HDMACNT1", "HDMA 1 Line Counter"],
	0x4320: ["DMAP2", "DMA 2 Control"],
	0x4321: ["DMADEST2", "DMA 2 Destination Register"],
	0x4322: ["DMASRC2L", "DMA 2 Source Adress Low Byte"],
	0x4323: ["DMASRC2H", "DMA 2 Source Address High Byte"],
	0x4324: ["DMASRC2B", "DMA 2 Source Address Bank"],
	0x4325: ["DMALEN2L", "DMA 2 Transfer Size Low Byte"],
	0x4326: ["DMALEN2H", "DMA 2 Transfer Size High Byte"],
	0x4327: ["DMALEN2B", "DMA 2 Transfer Bank"],
	0x4328: ["HDMATBL2L", "HDMA 2 Table Address Low Byte"],
	0x4329: ["HDMATBL2H", "HDMA 2 Table Address High Byte"],
	0x432a: ["HDMACNT2", "HDMA 2 Line Counter"],
	0x4330: ["DMAP3", "DMA 3 Control"],
	0x4331: ["DMADEST3", "DMA 3 Destination Register"],
	0x4332: ["DMASRC3L", "DMA 3 Source Adress Low Byte"],
	0x4333: ["DMASRC3H", "DMA 3 Source Address High Byte"],
	0x4334: ["DMASRC3B", "DMA 3 Source Address Bank"],
	0x4335: ["DMALEN3L", "DMA 3 Transfer Size Low Byte"],
	0x4336: ["DMALEN3H", "DMA 3 Transfer Size High Byte"],
	0x4337: ["DMALEN3B", "DMA 3 Transfer Bank"],
	0x4338: ["HDMATBL3L", "HDMA 3 Table Address Low Byte"],
	0x4339: ["HDMATBL3H", "HDMA 3 Table Address High Byte"],
	0x433a: ["HDMACNT3", "HDMA 3 Line Counter"],
	0x4340: ["DMAP4", "DMA 4 Control"],
	0x4341: ["DMADEST4", "DMA 4 Destination Register"],
	0x4342: ["DMASRC4L", "DMA 4 Source Adress Low Byte"],
	0x4343: ["DMASRC4H", "DMA 4 Source Address High Byte"],
	0x4344: ["DMASRC4B", "DMA 4 Source Address Bank"],
	0x4345: ["DMALEN4L", "DMA 4 Transfer Size Low Byte"],
	0x4346: ["DMALEN4H", "DMA 4 Transfer Size High Byte"],
	0x4347: ["DMALEN4B", "DMA 4 Transfer Bank"],
	0x4348: ["HDMATBL4L", "HDMA 4 Table Address Low Byte"],
	0x4349: ["HDMATBL4H", "HDMA 4 Table Address High Byte"],
	0x434a: ["HDMACNT4", "HDMA 4 Line Counter"],
	0x4350: ["DMAP5", "DMA 5 Control"],
	0x4351: ["DMADEST5", "DMA 5 Destination Register"],
	0x4352: ["DMASRC5L", "DMA 5 Source Adress Low Byte"],
	0x4353: ["DMASRC5H", "DMA 5 Source Address High Byte"],
	0x4354: ["DMASRC5B", "DMA 5 Source Address Bank"],
	0x4355: ["DMALEN5L", "DMA 5 Transfer Size Low Byte"],
	0x4356: ["DMALEN5H", "DMA 5 Transfer Size High Byte"],
	0x4357: ["DMALEN5B", "DMA 5 Transfer Bank"],
	0x4358: ["HDMATBL5L", "HDMA 5 Table Address Low Byte"],
	0x4359: ["HDMATBL5H", "HDMA 5 Table Address High Byte"],
	0x435a: ["HDMACNT5", "HDMA 5 Line Counter"],
	0x4360: ["DMAP6", "DMA 6 Control"],
	0x4361: ["DMADEST6", "DMA 6 Destination Register"],
	0x4362: ["DMASRC6L", "DMA 6 Source Adress Low Byte"],
	0x4363: ["DMASRC6H", "DMA 6 Source Address High Byte"],
	0x4364: ["DMASRC6B", "DMA 6 Source Address Bank"],
	0x4365: ["DMALEN6L", "DMA 6 Transfer Size Low Byte"],
	0x4366: ["DMALEN6H", "DMA 6 Transfer Size High Byte"],
	0x4367: ["DMALEN6B", "DMA 6 Transfer Bank"],
	0x4368: ["HDMATBL6L", "HDMA 6 Table Address Low Byte"],
	0x4369: ["HDMATBL6H", "HDMA 6 Table Address High Byte"],
	0x436a: ["HDMACNT6", "HDMA 6 Line Counter"],
	0x4370: ["DMAP7", "DMA 7 Control"],
	0x4371: ["DMADEST7", "DMA 7 Destination Register"],
	0x4372: ["DMASRC7L", "DMA 7 Source Adress Low Byte"],
	0x4373: ["DMASRC7H", "DMA 7 Source Address High Byte"],
	0x4374: ["DMASRC7B", "DMA 7 Source Address Bank"],
	0x4375: ["DMALEN7L", "DMA 7 Transfer Size Low Byte"],
	0x4376: ["DMALEN7H", "DMA 7 Transfer Size High Byte"],
	0x4377: ["DMALEN7B", "DMA 7 Transfer Bank"],
	0x4378: ["HDMATBL7L", "HDMA 7 Table Address Low Byte"],
	0x4379: ["HDMATBL7H", "HDMA 7 Table Address High Byte"],
	0x437a: ["HDMACNT7", "HDMA 7 Line Counter"]
}

class Disassembler:

	def __init__(self, cart, options={}):
		self.cart = cart
		self.options = options
		self.pos = 0
		self.flags = 0
		self.labels = set()
		self.data_labels = dict()
		self.code = OrderedDictRange()
		self.decoders = RangeTree()
		self.add_decoder(Headers(self.cart.header,self.cart.header+80))
		self.hex_comment = bool(self.options.hex)

	def run(self):
		print "Disassembling..."
		self.mark_vectors()

		self.run_decoders()

		if self.options.banks:
			for b in self.options.banks:
				if b < self.cart.bank_count():
					self.decode_bank(b)
				else:
					print("Invalid bank %d" % b)
		else:
			self.auto_run()

		self.fill_data_banks()

	def add_decoder(self, decoder):
		self.decoders.add(decoder.start, decoder.end, decoder)

	def run_decoders(self):
		for dec in self.decoders.items():
			for pos, instr in dec.decode(self.cart):
				self.code[pos] = instr

	# Mark header vectors as code labels
	def mark_vectors(self):
		vectors = ["nvec_unused", "nvec_cop", "nvec_brk", "nvec_abort", "nvec_nmi", "nvec_reset", "nvec_irq", "evec_unused", "evec_cop", "evec_unused2", "evec_abort", "evec_nmi", "evec_reset", "evec_irq"]

		for v in vectors:
			addr = getattr(self.cart, v)
			if (addr >= 0x8000):
				self.labels.add(addr-0x8000)

	def auto_run(self):
		self.decode(0, len(self.cart.data))
		
	def decode_bank(self, bank):
		start = self.cart.bank_size() * bank
		end = start + self.cart.bank_size()
		self.decode(start, end)
	
	def decode(self, start, end):

		self.pos = start
		while self.pos < end:

			op = self.cart[self.pos]
			op_size = self.opSize(op)

			# If intersects decoder
			decoder = self.decoders.intersects(self.pos, self.pos + op_size)
			if decoder:
				# Check if the last opcode intersected with decoder
				if self.pos + op_size > decoder.start:
					self.code[self.pos] = self.ins('.db ' + ', '.join(("$%02X" % x) for x in self.cart[self.pos : decoder.start - 1]), comment = 'Opcode overrunning decoder')
				self.pos = decoder.end
				continue

			# If opcode overruns bank boundry
			elif (self.cart.address(self.pos) & 0xFFFF) + op_size > 0xFFFF:
				self.code[self.pos] = self.ins(".db $%02X" % op, comment = "Opcode %02X overrunning bank boundry at %06X. Skipping." % (op, self.pos))
				self.pos = self.pos + 1
				continue
			
			# Decode op codes	
			func = getattr(self, 'op%02X' % op)
			if not func:
				self.code[self.pos] = self.ins(".db $%02X" % op, comment = "Unhandled opcode: %02X at %06X" % (op, self.pos))
				self.pos = self.pos + 1
				continue
			ins = func()

			if self.hex_comment:
				if op_size == 1:
					ins.comment = "%02X" % op
				elif op_size == 2:
					ins.comment = "%02X %02X" % (op, self.cart[self.pos + 1])
				elif op_size == 3:
					ins.comment = "%02X %02X %02X" % (op, self.cart[self.pos + 1], self.cart[self.pos + 2])
				elif op_size == 4:
					ins.comment = "%02X %02X %02X %02X" % (op, self.cart[self.pos + 1], self.cart[self.pos + 2], self.cart[self.pos + 3])

			self.code[self.pos] = ins
			self.pos = self.pos + op_size

	def fill_data_banks(self):
		for bank in range(0, self.cart.bank_count()):
			addr = bank * self.cart.bank_size()
			if self.code.get(addr) == None:
				self.make_data_bank(bank)

	def make_data_bank(self, bank):
		start = bank * self.cart.bank_size()
		end = start + self.cart.bank_size()

		for y in range(start, end, 16):
			line = '.db ' + ', '.join(("$%02X" % x) for x in self.cart[y : y+16])
			self.code[y] = self.ins(line)

	def assembly(self):
		code = ""
		bank = 0
		# Ensure code is ordered
		self.code.sort_keys()

		# Process each bank
		for addr in range(0, self.cart.size(), self.cart.bank_size() ):
			print "Bank %d" % bank
			if bank == 0:
				code = code + ".BANK %d SLOT 0\n.ORG $0000\n\n.SECTION \"Bank%d\" FORCE\n\n" % (bank, bank)
			else:
				code = code + ".ENDS\n\n.BANK %d SLOT 0\n.ORG $0000\n\n.SECTION \"Bank%d\" FORCE\n\n" % (bank, bank)

			for addr, instr in self.code.item_range(addr, addr+self.cart.bank_size()):
				if addr in self.labels:
					code = code + "L%06X:\n" % addr
				code = code + str(instr) + "\n"

			bank = bank + 1

		code = code + ".ENDS\n"
		return code

	def valid_label(self, index):

		if (index < self.pos):
			return index in self.code
		else:
			# Read ahead to find valid opcode index
			flags = self.flags
			pos = self.pos
			valid = False
			while self.pos <= index:
				op = self.cart[self.pos]
				# Follow flag changes
				if op == 0xC2:
					self.opC2()
				elif op == 0xE2:
					self.opE2()
				self.pos = self.pos + self.opSize(op)
				if index == self.pos:
					valid = True
					break

			self.pos = pos
			self.flags = flags
			return valid

	def acc16(self):
		return self.flags & 0x20 == 0

	def ind16(self):
		return self.flags & 0x10 == 0

	def set_label(self, address):
		self.labels.add(address)

	# Append instruction
	def ins(self, code, preamble=None, comment=None):
		return Instruction(code,preamble,comment)

	def opSize(self, op):
		size = InstructionSizes[op]
		# Calculate variable size instructions from accumulator state
		if self.acc16() and op in [0x09,0x69, 0x29, 0x89, 0xC9, 0x49, 0xE9, 0xA9]:
			size = size + 1
		elif self.ind16() and op in [0xE0, 0xC0, 0xA2, 0xA0]:
			size = size + 1
		return size

	def op01(self):
		return self.ins("ora" + self.dir_page_ind_indir_x())

	# ADC
	def op69(self):
		return self.ins("adc" + self.immediate())

	def op6D(self):
		return self.ins("adc" + self.abs())

	def op6F(self):
		return self.ins("adc" + self.abs_long())

	def op65(self):
		return self.ins("adc" + self.dir_page())

	def op72(self):
		return self.ins("adc" + self.dir_page_indir())

	def op67(self):
		return self.ins("adc" + self.dir_page_indir_long())

	def op7D(self):
		return self.ins("adc" + self.abs_ind_x())

	def op7F(self):
		return self.ins("adc" + self.abs_long_ind_x())

	def op79(self):
		return self.ins("adc" + self.abs_ind_y())

	def op75(self):
		return self.ins("adc" + self.dir_page_ind_x())

	def op61(self):
		return self.ins("adc" + self.dir_page_ind_indir_x())

	def op71(self):
		return self.ins("adc" + self.dir_page_ind_indir_y())

	def op77(self):
		return self.ins("adc" + self.dir_page_indir_long_y())

	def op63(self):
		return self.ins("adc" + self.stack_rel())

	def op73(self):
		return self.ins("adc" + self.stack_rel_indir_y())

	# AND
	def op29(self):
		return self.ins("and" + self.immediate())

	def op2D(self):
		return self.ins("and" + self.abs())

	def op2F(self):
		return self.ins("and" + self.abs_long())

	def op25(self):
		return self.ins("and" + self.dir_page())

	def op32(self):
		return self.ins("and" + self.dir_page_indir())

	def op27(self):
		return self.ins("and" + self.dir_page_indir_long())

	def op3D(self):
		return self.ins("and" + self.abs_ind_x())

	def op3F(self):
		return self.ins("and" + self.abs_long_ind_x())

	def op39(self):
		return self.ins("and" + self.abs_ind_y())

	def op35(self):
		return self.ins("and" + self.dir_page_ind_x())

	def op21(self):
		return self.ins("and" + self.dir_page_ind_indir_x())

	def op31(self):
		return self.ins("and" + self.dir_page_ind_indir_y())

	def op37(self):
		return self.ins("and" + self.dir_page_indir_long_y())

	def op23(self):
		return self.ins("and" + self.stack_rel())

	def op33(self):
		return self.ins("and" + self.stack_rel_indir_y())

	# ASL
	def op0A(self):
		return self.ins("asl A")

	def op0E(self):
		return self.ins("asl" + self.abs())

	def op06(self):
		return self.ins("asl" + self.dir_page())

	def op1E(self):
		return self.ins("asl" + self.abs_ind_x())

	def op16(self):
		return self.ins("asl" + self.dir_page_ind_x())

	# BCC
	def op90(self):
		return self.branch("bcc")
 
 	# BCS
	def opB0(self):
		return self.branch("bcs")
 
 	# BEQ
	def opF0(self):
		return self.branch("beq")
 
 	# BNE
	def opD0(self):
		return self.branch("bne")
 
 	# BMI
	def op30(self):
		return self.branch("bmi")
 
 	# BPL
	def op10(self):
		return self.branch("bpl")
 
 	# BVC
	def op50(self):
		return self.branch("bvc")
 
 	# BVS
	def op70(self):
		return self.branch("bvs")
 
 	# BRA
	def op80(self):
		return self.branch("bra")
 
 	# BRL
	def op82(self):
		return self.pc_rel_long("brl")

	# BIT
	def op89(self):
		return self.ins("bit" + self.immediate())

	def op2C(self):
		return self.ins("bit" + self.abs())

	def op24(self):
		return self.ins("bit" + self.dir_page())

	def op3C(self):
		return self.ins("bit" + self.abs_ind_x())

	def op34(self):
		return self.ins("bit" + self.dir_page_ind_x())
 
 	# BRK
	def op00(self):
		return self.ins("brk" + self.stack_interrupt())
 
 	# CLC
	def op18(self):
		return self.ins("clc")
 
 	# CLD
	def opD8(self):
		return self.ins("cld")
 
 	# CLI
	def op58(self):
		return self.ins("cli")
 
 	# CLV
	def opB8(self):
		return self.ins("clv")
 
 	# SEC
	def op38(self):
		return self.ins("sec")
 
 	# SED
	def opF8(self):
		return self.ins("sed")
 
 	# SEI
	def op78(self):
		return self.ins("sei")

	# CMP
	def opC9(self):
		return self.ins("cmp" + self.immediate())

	def opCD(self):
		return self.ins("cmp" + self.abs())

	def opCF(self):
		return self.ins("cmp" + self.abs_long())

	def opC5(self):
		return self.ins("cmp" + self.dir_page())

	def opD2(self):
		return self.ins("cmp" + self.dir_page_indir())

	def opC7(self):
		return self.ins("cmp" + self.dir_page_indir_long())

	def opDD(self):
		return self.ins("cmp" + self.abs_ind_x())

	def opDF(self):
		return self.ins("cmp" + self.abs_long_ind_x())

	def opD9(self):
		return self.ins("cmp" + self.abs_ind_y())

	def opD5(self):
		return self.ins("cmp" + self.dir_page_ind_x())

	def opC1(self):
		return self.ins("cmp" + self.dir_page_ind_indir_x())

	def opD1(self):
		return self.ins("cmp" + self.dir_page_ind_indir_y())

	def opD7(self):
		return self.ins("cmp" + self.dir_page_indir_long_y())

	def opC3(self):
		return self.ins("cmp" + self.stack_rel())

	def opD3(self):
		return self.ins("cmp" + self.stack_rel_indir_y())

	# COP
	def op02(self):
		return self.ins("cop" + self.stack_interrupt())

	# CPX
	def opE0(self):
		return self.ins("cpx" + self.immediate_ind())

	def opEC(self):
		return self.abs_lookup("cpx")

	def opE4(self):
		return self.ins("cpx" + self.dir_page())

	# CPY
	def opC0(self):
		return self.ins("cpy" + self.immediate_ind())

	def opCC(self):
		return self.abs_lookup("cpy")

	def opC4(self):
		return self.ins("cpy" + self.dir_page())

	# DEC
	def op3A(self):
		return self.ins("dec A")

	def opCE(self):
		return self.abs_lookup("dec")

	def opC6(self):
		return self.ins("dec" + self.dir_page())

	def opDE(self):
		return self.ins("dec" + self.abs_ind_x())

	def opD6(self):
		return self.ins("dec" + self.dir_page_ind_x())

	# DEX
	def opCA(self):
		return self.ins("dex")

	# DEY
	def op88(self):
		return self.ins("dey")

	# EOR
	def op49(self):
		return self.ins("eor" + self.immediate())

	def op4D(self):
		return self.abs_lookup("eor")

	def op4F(self):
		return self.ins("eor" + self.abs_long())

	def op45(self):
		return self.ins("eor" + self.dir_page())

	def op52(self):
		return self.ins("eor" + self.dir_page_indir())

	def op47(self):
		return self.ins("eor" + self.dir_page_indir_long())

	def op5D(self):
		return self.ins("eor" + self.abs_ind_x())

	def op5F(self):
		return self.ins("eor" + self.abs_long_ind_x())

	def op59(self):
		return self.ins("eor" + self.abs_ind_y())

	def op55(self):
		return self.ins("eor" + self.dir_page_ind_x())

	def op41(self):
		return self.ins("eor" + self.dir_page_ind_indir_x())

	def op51(self):
		return self.ins("eor" + self.dir_page_ind_indir_y())

	def op57(self):
		return self.ins("eor" + self.dir_page_indir_long_y())

	def op43(self):
		return self.ins("eor" + self.stack_rel())

	def op53(self):
		return self.ins("eor" + self.stack_rel_indir_y())

	# INC
	def op1A(self):
		return self.ins("inc A")

	def opEE(self):
		return self.abs_lookup("inc")

	def opE6(self):
		return self.ins("inc" + self.dir_page())

	def opFE(self):
		return self.ins("inc" + self.abs_ind_x())

	def opF6(self):
		return self.ins("inc" + self.dir_page_ind_x())

	# INX
	def opE8(self):
		return self.ins("inx")

	# INY
	def opC8(self):
		return self.ins("iny")

	# JMP
	def op4C(self):
		pipe = self.pipe16()

		if self.cart.hirom:
			address = (self.pos & 0xFF0000) | pipe
		else:
			# If invalid lorom bank
			if pipe < 0x8000:
				return self.ins("jmp $%04X" % pipe)
			else:
				address = (self.pos & 0xFF0000) | (pipe - 0x8000)
		if self.valid_label(address):
			self.set_label(address) 
			return self.ins("jmp L%06X" % address)
		else:
			return self.ins("jmp $%04X" % pipe)

	def op6C(self):
		return self.ins("jmp" + self.abs_indir())

	def op7C(self):
		return self.ins("jmp" + self.abs_ind_indir())

	def op5C(self):
		#TODO
		#self.set_label( self.pipe24() ) 
		return self.ins("jmp" + self.abs_long())

	def opDC(self):
		return self.ins("jmp" + self.abs_indir_long())

	# JSR
	def op22(self):
		#TODO
		#self.set_label( self.pipe24() ) 
		return self.ins("jsr" + self.abs_long())

	def op20(self):
		self.set_label( (self.pos & 0xFF0000) | self.pipe16() ) 
		return self.ins("jsr" + self.abs())

	def opFC(self):
		return self.ins("jsr" + self.abs_ind_indir())

	# LDA
	def opA9(self):
		return self.ins("lda" + self.immediate())

	def opAD(self):
		return self.abs_lookup("lda")

	def opAF(self):
		return self.ins("lda" + self.abs_long())

	def opA5(self):
		return self.ins("lda" + self.dir_page())

	def opB2(self):
		return self.ins("lda" + self.dir_page_indir())

	def opA7(self):
		return self.ins("lda" + self.dir_page_indir_long())

	def opBD(self):
		return self.ins("lda" + self.abs_ind_x())

	def opBF(self):
		return self.ins("lda" + self.abs_long_ind_x())

	def opB9(self):
		return self.ins("lda" + self.abs_ind_y())

	def opB5(self):
		return self.ins("lda" + self.dir_page_ind_x())

	def opA1(self):
		return self.ins("lda" + self.dir_page_ind_indir_x())

	def opB1(self):
		return self.ins("lda" + self.dir_page_ind_indir_y())

	def opB7(self):
		return self.ins("lda" + self.dir_page_indir_long_y())

	def opA3(self):
		return self.ins("lda" + self.stack_rel())

	def opB3(self):
		return self.ins("lda" + self.stack_rel_indir_y())

	# LDX
	def opA2(self):
		return self.ins("ldx" + self.immediate_ind())

	def opAE(self):
		return self.abs_lookup("ldx")

	def opA6(self):
		return self.ins("ldx" + self.dir_page())

	def opBE(self):
		return self.ins("ldx" + self.abs_ind_y())

	def opB6(self):
		return self.ins("ldx" + self.dir_page_ind_y())

	# LDY
	def opA0(self):
		return self.ins("ldy" + self.immediate_ind())

	def opAC(self):
		return self.abs_lookup("ldy")

	def opA4(self):
		return self.ins("ldy" + self.dir_page())

	def opBC(self):
		return self.ins("ldy" + self.abs_ind_x())

	def opB4(self):
		return self.ins("ldy" + self.dir_page_ind_x())

	# LSR
	def op4A(self):
		return self.ins("lsr A")

	def op4E(self):
		return self.abs_lookup("lsr")

	def op46(self):
		return self.ins("lsr" + self.dir_page())

	def op5E(self):
		return self.ins("lsr" + self.abs_ind_x())

	def op56(self):
		return self.ins("lsr" + self.dir_page_ind_x())

	# MVN
	def op54(self):
		return self.ins("mvn" + self.block_move())

	# MVP
	def op44(self):
		return self.ins("mvp" + self.block_move())

	# NOP
	def opEA(self):
		return self.ins("nop")

	# ORA
	def op09(self):
		return self.ins("ora" + self.immediate())

	def op0D(self):
		return self.abs_lookup("ora")

	def op0F(self):
		return self.ins("ora" + self.abs_long())

	def op05(self):
		return self.ins("ora" + self.dir_page())

	def op12(self):
		return self.ins("ora" + self.dir_page_indir())

	def op07(self):
		return self.ins("ora" + self.dir_page_indir_long())

	def op1D(self):
		return self.ins("ora" + self.abs_ind_x())

	def op1F(self):
		return self.ins("ora" + self.abs_long_ind_x())

	def op19(self):
		return self.ins("ora" + self.abs_ind_y())

	def op15(self):
		return self.ins("ora" + self.dir_page_ind_x())

	def op01(self):
		return self.ins("ora" + self.dir_page_ind_indir_x())

	def op11(self):
		return self.ins("ora" + self.dir_page_ind_indir_y())

	def op17(self):
		return self.ins("ora" + self.dir_page_indir_long_y())

	def op03(self):
		return self.ins("ora" + self.stack_rel())

	def op13(self):
		return self.ins("ora" + self.stack_rel_indir_y())

 	# PEA
	def opF4(self):
		return self.ins("pea" + self.abs())
 
 	# PEI
	def opD4(self):
		return self.ins("pei" + self.dir_page_indir())
 
 	# PER
	def op62(self):
		return self.pc_rel_long("per")
 
 	# PHA
	def op48(self):
		return self.ins("pha")
 
 	# PHP
	def op08(self):
		return self.ins("php")
 
 	# PHX
	def opDA(self):
		return self.ins("phx")
 
 	# PHY
	def op5A(self):
		return self.ins("phy")
 
 	# PLA
	def op68(self):
		return self.ins("pla")
 
 	# PLP
	def op28(self):
		return self.ins("plp")
 
 	# PLX
	def opFA(self):
		return self.ins("plx")
 
 	# PLY
	def op7A(self):
		return self.ins("ply")
 
 	# PHB
	def op8B(self):
		return self.ins("phb")
 
 	# PHD
	def op0B(self):
		return self.ins("phd")
 
 	# PHK
	def op4B(self):
		return self.ins("phk")
 
 	# PLB
	def opAB(self):
		return self.ins("plb")
 
 	# PLD
	def op2B(self):
		return self.ins("pld")

	# REP
	def opC2(self):
		val = self.pipe8()
		self.flags = self.flags & (~val)
		pre = None
		if val & 0x20:
			pre = ".ACCU 16"
		if val & 0x10:
			pre = pre + "\n" if pre else ""
			pre = pre + ".INDEX 16"
		return self.ins("rep #$%02X" % self.pipe8(), pre )

	# SEP
	def opE2(self):
		val = self.pipe8()
		self.flags = self.flags | val
		pre = None
		if val & 0x20:
			pre = ".ACCU 8"
		if val & 0x10:
			pre = pre + "\n" if pre else ""
			pre = pre + ".INDEX 8"
		return self.ins("sep #$%02X" % self.pipe8(), pre )

	# ROL
	def op2A(self):
		return self.ins("rol A")

	def op2E(self):
		return self.abs_lookup("rol")

	def op26(self):
		return self.ins("rol" + self.dir_page())

	def op3E(self):
		return self.ins("rol" + self.abs_ind_x())

	def op36(self):
		return self.ins("rol" + self.dir_page_ind_x())

	# ROR
	def op6A(self):
		return self.ins("ror A")

	def op6E(self):
		return self.abs_lookup("ror")

	def op66(self):
		return self.ins("ror" + self.dir_page())

	def op7E(self):
		return self.ins("ror" + self.abs_ind_x())

	def op76(self):
		return self.ins("ror" + self.dir_page_ind_x())

	# RTI
	def op40(self):
		return self.ins("rti")

	# RTL
	def op6B(self):
		return self.ins("rtl")

	# RTS
	def op60(self):
		return self.ins("rts")

	# SBC
	def opE9(self):
		return self.ins("sbc" + self.immediate())

	def opED(self):
		return self.abs_lookup("sbc")

	def opEF(self):
		return self.ins("sbc" + self.abs_long())

	def opE5(self):
		return self.ins("sbc" + self.dir_page())

	def opF2(self):
		return self.ins("sbc" + self.dir_page_indir())

	def opE7(self):
		return self.ins("sbc" + self.dir_page_indir_long())

	def opFD(self):
		return self.ins("sbc" + self.abs_ind_x())

	def opFF(self):
		return self.ins("sbc" + self.abs_long_ind_x())

	def opF9(self):
		return self.ins("sbc" + self.abs_ind_y())

	def opF5(self):
		return self.ins("sbc" + self.dir_page_ind_x())

	def opE1(self):
		return self.ins("sbc" + self.dir_page_ind_indir_x())

	def opF1(self):
		return self.ins("sbc" + self.dir_page_ind_indir_y())

	def opF7(self):
		return self.ins("sbc" + self.dir_page_indir_long_y())

	def opE3(self):
		return self.ins("sbc" + self.stack_rel())

	def opF3(self):
		return self.ins("sbc" + self.stack_rel_indir_y())

	# STA
	def op8D(self):
		return self.abs_lookup("sta")

	def op8F(self):
		return self.ins("sta" + self.abs_long())

	def op85(self):
		return self.ins("sta" + self.dir_page())

	def op92(self):
		return self.ins("sta" + self.dir_page_indir())

	def op87(self):
		return self.ins("sta" + self.dir_page_indir_long())

	def op9D(self):
		return self.ins("sta" + self.abs_ind_x())

	def op9F(self):
		return self.ins("sta" + self.abs_long_ind_x())

	def op99(self):
		return self.ins("sta" + self.abs_ind_y())

	def op95(self):
		return self.ins("sta" + self.dir_page_ind_x())

	def op81(self):
		return self.ins("sta" + self.dir_page_ind_indir_x())

	def op91(self):
		return self.ins("sta" + self.dir_page_ind_indir_y())

	def op97(self):
		return self.ins("sta" + self.dir_page_indir_long_y())

	def op83(self):
		return self.ins("sta" + self.stack_rel())

	def op93(self):
		return self.ins("sta" + self.stack_rel_indir_y())

	# STP
	def opDB(self):
		return self.ins("stp")

	# STX
	def op8E(self):
		return self.abs_lookup("stx")

	def op86(self):
		return self.ins("stx" + self.dir_page())

	def op96(self):
		return self.ins("stx" + self.dir_page_ind_y())

	# STY
	def op8C(self):
		return self.abs_lookup("sty")

	def op84(self):
		return self.ins("sty" + self.dir_page())

	def op94(self):
		return self.ins("sty" + self.dir_page_ind_x())

	# STZ
	def op9C(self):
		return self.abs_lookup("stz")

	def op64(self):
		return self.ins("stz" + self.dir_page())

	def op9E(self):
		return self.ins("stz" + self.abs_ind_x())

	def op74(self):
		return self.ins("stz" + self.dir_page_ind_x())

 	# TAX
	def opAA(self):
		return self.ins("tax")
 
 	# TAY
	def opA8(self):
		return self.ins("tay")
 
 	# TXA
	def op8A(self):
		return self.ins("txa")
 
 	# TYA
	def op98(self):
		return self.ins("tya")
 
 	# TSX
	def opBA(self):
		return self.ins("tsx")
 
 	# TXS
	def op9A(self):
		return self.ins("txs")
 
 	# TXY
	def op9B(self):
		return self.ins("txy")
 
 	# TYX
	def opBB(self):
		return self.ins("tyx")
 
 	# TCD
	def op5B(self):
		return self.ins("tcd")
 
 	# TDC
	def op7B(self):
		return self.ins("tdc")

 	# TCS
	def op1B(self):
		return self.ins("tcs")
 
 	# TSC
	def op3B(self):
		return self.ins("tsc")
 
 	# TRB
	def op1C(self):
		return self.abs_lookup("trb")

	def op14(self):
		return self.ins("trb" + self.dir_page())
 
 	# TSB
	def op0C(self):
		return self.abs_lookup("tsb")

	def op04(self):
		return self.ins("tsb" + self.dir_page())
 
 	# WAI
	def opCB(self):
		return self.ins("wai")
 
 	# WDM
	def op42(self):
		return self.ins(".db $42, $%02X" % self.pipe8(), comment = "opcode wdm $%02X" % self.pipe8())
 
 	# XBA
	def opEB(self):
		return self.ins("xba")
 
 	# XCE
	def opFB(self):
		return self.ins("xce")

	# Address modes

	def immediate(self):
		if self.acc16():
			return " #$%04X.w" % self.pipe16()
		else:
			return " #$%02X.b" % self.pipe8()

	def immediate_ind(self):
		if self.ind16():
			return " #$%04X.w" % self.pipe16()
		else:
			return " #$%02X.b" % self.pipe8()

	def abs(self):
		return " $%04X.w" % self.pipe16()

	def abs_lookup(self, op):
		address = self.pipe16()
		address_info = StaticAddresses.get(address)

		if address_info:
			return self.ins(op + " " + address_info[0] + ".w", comment = address_info[1])
		else:
			return self.ins(op + self.abs())

	def abs_indir(self):
		return " ($%04X.w)" % self.pipe16()

	def abs_ind_indir(self):
		return " ($%04X.w,X)" % self.pipe16()

	def abs_indir_long(self):
		return " [$%04X.w]" % self.pipe16()

	def abs_ind_x(self):
		return " $%04X.w,X" % self.pipe16()

	def abs_ind_y(self):
		return " $%04X.w,Y" % self.pipe16()

	def abs_long(self):
		return " $%06X.l" % self.pipe24()
	
	def abs_long_ind_x(self):
		return " $%06X.l,X" % self.pipe24()

	def dir_page(self):
		return " $%02X.b" % self.pipe8()

	def dir_page_indir(self):
		return " ($%02X.b)" % self.pipe8()

	def dir_page_ind_x(self):
		return " $%02X.b,X" % self.pipe8()

	def dir_page_ind_y(self):
		return " $%02X.b,Y" % self.pipe8()

	def dir_page_indir_long(self):
		return " [$%02X.b]" % self.pipe8()

	def dir_page_ind_indir_x(self):
		return " ($%02X.b,X)" % self.pipe8()

	def dir_page_ind_indir_y(self):
		return " ($%02X.b),Y" % self.pipe8()

	def dir_page_indir_long_y(self):
		return " [$%02X.b],Y" % self.pipe8()

	def stack_rel(self):
		return " $%02X.b,S" % self.pipe8()

	def stack_rel_indir_y(self):
		return " ($%02X.b,S),Y" % self.pipe8()

	def stack_interrupt(self):
		return " $%02X.b" % self.pipe8()

	def block_move(self):
		return " $%02X,$%02X" % (self.cart[self.pos+2], self.cart[self.pos+1])

	def branch(self, type):
		val = self.pipe8()
		if val > 127:
			val = val - 256
		address = (self.pos & 0xFF0000 ) + ((self.pos + val + 2) & 0xFFFF)

		# If jump wraps bank
		if not self.cart.hirom and ((self.pos & 0x7FFF) + val + 2) & 0x8000:
			return self.ins(".db $%02X, $%02X" % (self.cart[self.pos], self.pipe8()), comment="Invalid bank wrapping branch target (%s L%06X)" % (type, address))

		if self.valid_label(address):
			self.set_label( address )
			return self.ins("%s L%06X" % (type, address)) 
		else:
			return self.ins(".db $%02X, $%02X" % (self.cart[self.pos], self.pipe8()), comment="Invalid branch target (%s L%06X)" % (type, address))

	def pc_rel_long(self, ins):
		val = self.pipe16()
		if val > 32767:
			val = val - 65536

		# If jump is into lower invalid lorom address space (address < 0x8000)
		if not self.cart.hirom and ((self.pos & 0x7FFF) + val + 3) & 0x8000:
			return self.ins("%s $%04X" % (ins, 0xFFFF & val ), comment='Invalid branch target' )

		address = (self.pos & 0xFF0000 ) + ((self.pos + val + 3) & 0xFFFF)

		if self.valid_label(address):
			self.set_label( address )
			return self.ins("%s L%06X" % (ins, address))
		else:
			return self.ins("%s $%04X" % (ins, 0xFFFF & val))

	def pipe8(self):
		return self.cart[self.pos+1]

	def pipe16(self):
		return self.cart[self.pos+1] | (self.cart[self.pos+2] << 8)

	def pipe24(self):
		return self.cart[self.pos+1] | (self.cart[self.pos+2] << 8) | (self.cart[self.pos+3] << 16)

class Decoder:
	def __init__(self, label, start, end):
		self.label = label
		self.start = start
		self.end = end

	def name(self):
		return "%s%06x-%06x" % (self.__name__, self.start, self.end)

	def decode(self, cart):
		show_comment = self.comment != None
		for y in range(self.start, self.end, 16):
			line = '.db ' + ', '.join(("$%02X" % x) for x in cart[y : min(y+16, self.end)])
			if show_comment:
				yield (y, Instruction(line, comment=self.comment))
				show_comment = False
			else:
				yield (y, Instruction(line))

class Headers(Decoder):
	def __init__(self, start, end):
		Decoder.__init__(self, "Headers", start, end)

	def decode(self, cart):
		yield (self.start, Instruction('; Auto-generated headers', preamble=self.label+":"))

class TextDecoder(Decoder):
	def __init__(self, label, start, end, pack=None):
		Decoder.__init__(self, label, start, end)
		self.pack = pack
		if self.pack != None:
			if type(self.pack) is not list:
				raise ValueError("TextDecoder: pack parameter is not an array")

	def decode(self, cart):
		if self.pack == None:
			string = ''.join( chr(x) for x in cart[self.start : self.end])
			line = '.db "%s"' % ansi_escape(string)
			yield (self.start, Instruction(line, preamble=self.label+":"))
		else:
			pos = self.start
			for (label, size) in self.pack:
				string = ''.join( chr(x) for x in cart[pos : pos + size])
				line = '.db "%s"' % ansi_escape(string)
				yield (pos, Instruction(line, preamble=label+":"))
				pos = pos + size

class Instruction:
	def __init__(self, code, preamble=None, comment=None):
		self.code = code
		self.comment = comment
		self.preamble = preamble

	def __str__(self):
		return (self.preamble + "\n" if self.preamble else "") + "\t" + self.code + ( "\t\t; " + self.comment if self.comment else "")


class OrderedDictRange(OrderedDict):

	def sort_keys(self):
		keys = self.keys()
		keys.sort()
		dict_sort = OrderedDictRange((k, self[k]) for k in keys)
		self.clear()
		self.update(dict_sort)

	# Data slicing
	def item_range(self, start, stop):
		keys = self.keys()
		left = bisect.bisect_left(keys, start)
		right = bisect.bisect_left(keys, stop, left)
		return [ (k, self[k]) for k in keys[left:right] ]

_ESCAPE_CHARS = {'\t': '\\t', '\n': '\\n', '\r': '\\r', '\x0b': '\\x0b', '\x0c': '\\x0c', '"': '\\"', '\x00': '\\' + '0'}

def ansi_escape(subject):
	return ''.join([ _ESCAPE_CHARS[i] if i in _ESCAPE_CHARS else i for i in subject])

