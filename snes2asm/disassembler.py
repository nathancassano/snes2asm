import snes2asm
from collections import OrderedDict

from snes2asm.cartridge import Cartridge

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

class Disassembler:

	def __init__(self, cart, options={}):
		self.cart = cart
		self.options = options
		self.pos = 0
		self.flags = 0
		self.labels = set()
		self.code = OrderedDict()

	def run(self):
		if self.options.banks:
			for b in self.options.banks:
				if b < self.cart.bank_count():
					self.decode_bank(b)
				else:
					print("Invalid bank %d" % b)
		else:
			self.auto_run()

		self.fill_data_banks()

	def auto_run(self):

		# Decode first bank
		self.decode_bank(0)	

		while True:
			remaining = False 
			for label in self.labels.copy():
				bank = self.cart.bank_from_label(label)
				if self.banks[bank] == None:
					remaining = True
					self.decode_bank(bank)

			if not remaining:
				break

	def decode_bank(self, bank):
		start = self.cart.bank_size() * bank
		end = start + self.cart.bank_size()
		self.decode(start, end)
	
	def decode(self, start, end):

		self.pos = start
		while self.pos < end:
			op = self.cart[self.pos]
			op_size = self.opSize(op)

			if (self.cart.address(self.pos) & 0xFFFF) + op_size > 0xFFFF:
				print(";Opcode %02X overrunning bank boundry at %X. Skipping." % (op, self.pos))
				self.code[self.pos] = self.ins(".db $%02X" % op)
				self.pos = self.pos + 1
				continue
				
			func = getattr(self, 'op%02X' % op)
			if not func:
				print(";Unhandled opcode: %02X at %X" % (op, self.pos))
				self.code[self.pos] = self.ins(".db $%02X" % op)
				self.pos = self.pos + 1
				continue
			self.code[self.pos] = func()
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
		for addr, instr in self.code.items():
			if addr in self.labels:
				code = code + "L%06X:\n" % addr
			code = code + str(instr) + "\n"
		return code

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
		return self.ins("bcc" + self.branch())
 
 	# BCS
	def opB0(self):
		return self.ins("bcs" + self.branch())
 
 	# BEQ
	def opF0(self):
		return self.ins("beq" + self.branch())
 
 	# BNE
	def opD0(self):
		return self.ins("bne" + self.branch())
 
 	# BMI
	def op30(self):
		return self.ins("bmi" + self.branch())
 
 	# BPL
	def op10(self):
		return self.ins("bpl" + self.branch())
 
 	# BVC
	def op50(self):
		return self.ins("bvc" + self.branch())
 
 	# BVS
	def op70(self):
		return self.ins("bvs" + self.branch())
 
 	# BRA
	def op80(self):
		return self.ins("bra" + self.branch())
 
 	# BRL
	def op82(self):
		return self.ins("brl" + self.pc_rel_long())

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
		return self.ins("cpx" + self.abs())

	def opE4(self):
		return self.ins("cpx" + self.dir_page())

	# CPY
	def opC0(self):
		return self.ins("cpy" + self.immediate_ind())

	def opCC(self):
		return self.ins("cpy" + self.abs())

	def opC4(self):
		return self.ins("cpy" + self.dir_page())

	# DEC
	def op3A(self):
		return self.ins("dec A")

	def opCE(self):
		return self.ins("dec" + self.abs())

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
		return self.ins("eor" + self.abs())

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
		return self.ins("inc" + self.abs())

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
		address = (self.pos + 0xFF0000) | self.pipe16()
		self.set_label( address ) 
		return self.ins("jmp L%06X" % address)

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
		return self.ins("lda" + self.abs())

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
		return self.ins("ldx" + self.abs())

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
		return self.ins("ldy" + self.abs())

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
		return self.ins("lsr" + self.abs())

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
		return self.ins("ora" + self.abs())

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
		return self.ins("per" + self.pc_rel_long())
 
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
		return self.ins("rol" + self.abs())

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
		return self.ins("ror" + self.abs())

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
		return self.ins("sbc" + self.abs())

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
		return self.ins("sta" + self.abs())

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
		return self.ins("stx" + self.abs())

	def op86(self):
		return self.ins("stx" + self.dir_page())

	def op96(self):
		return self.ins("stx" + self.dir_page_ind_y())

	# STY
	def op8C(self):
		return self.ins("sty" + self.abs())

	def op84(self):
		return self.ins("sty" + self.dir_page())

	def op94(self):
		return self.ins("sty" + self.dir_page_ind_x())

	# STZ
	def op9C(self):
		return self.ins("stz" + self.abs())

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
		return self.ins("trb" + self.abs())

	def op14(self):
		return self.ins("trb" + self.dir_page())
 
 	# TSB
	def op0C(self):
		return self.ins("tsb" + self.abs())

	def op04(self):
		return self.ins("tsb" + self.dir_page())
 
 	# WAI
	def opCB(self):
		return self.ins("wai")
 
 	# WDM
	def op42(self):
		return self.ins("wdm" + " $%02X" % self.pipe8())
 
 	# XBA
	def opEB(self):
		return self.ins("xba")
 
 	# XCE
	def opFB(self):
		return self.ins("xce")

	# Address modes

	def immediate(self):
		if self.acc16():
			return " #$%04X" % self.pipe16()
		else:
			return " #$%02X" % self.pipe8()

	def immediate_ind(self):
		if self.ind16():
			return " #$%04X" % self.pipe16()
		else:
			return " #$%02X" % self.pipe8()

	def abs(self):
		return " $%04X" % self.pipe16()

	def abs_indir(self):
		return " ($%04X)" % self.pipe16()

	def abs_ind_indir(self):
		return " ($%04X,X)" % self.pipe16()

	def abs_indir_long(self):
		return " [$%04X]" % self.pipe16()

	def abs_ind_x(self):
		return " $%04X,X" % self.pipe16()

	def abs_ind_y(self):
		return " $%04X,Y" % self.pipe16()

	def abs_long(self):
		return " $%06X" % self.pipe24()
	
	def abs_long_ind_x(self):
		return " $%06X,X" % self.pipe24()

	def dir_page(self):
		return " $%02X" % self.pipe8()

	def dir_page_indir(self):
		return " ($%02X)" % self.pipe8()

	def dir_page_ind_x(self):
		return " $%02X,X" % self.pipe8()

	def dir_page_ind_y(self):
		return " $%02X,Y" % self.pipe8()

	def dir_page_indir_long(self):
		return " [$%02X]" % self.pipe8()

	def dir_page_ind_indir_x(self):
		return " ($%02X,X)" % self.pipe8()

	def dir_page_ind_indir_y(self):
		return " ($%02X),Y" % self.pipe8()

	def dir_page_indir_long_y(self):
		return " [$%02X],Y" % self.pipe8()

	def stack_rel(self):
		return " $%02X,S" % self.pipe8()

	def stack_rel_indir_y(self):
		return " ($%02X,S),Y" % self.pipe8()

	def stack_interrupt(self):
		return " $%02X" % self.pipe8()

	def block_move(self):
		return "$%02X,$%02X" % (self.cart[self.pos+1], self.cart[self.pos+2])

	def branch(self):
		val = self.pipe8()
		if val > 127:
			val = val - 256
		address = (self.pos & 0xFF0000 ) + ((self.pos + val + 2) & 0xFFFF)
		self.set_label( address )
		return " L%06X" % address

	def pc_rel_long(self):
		val = self.pipe16()
		if val > 32767:
			val = val - 65536
		address = (self.pos & 0xFF0000 ) + ((self.pos + val + 3) & 0xFFFF)
		self.set_label( address )
		return " L%06X" % address

	def pipe8(self):
		return self.cart[self.pos+1]

	def pipe16(self):
		return self.cart[self.pos+1] | (self.cart[self.pos+2] << 8)

	def pipe24(self):
		return self.cart[self.pos+1] | (self.cart[self.pos+2] << 8) | (self.cart[self.pos+3] << 16)

	def output(self, path):
		pass


class Instruction:
	def __init__(self, code, preamble=None, comment=None):
		self.code = code
		self.comment = comment
		self.preamble = preamble

	def __str__(self):
		return (self.preamble + "\n" if self.preamble else "") + "\t" + self.code + ( "  " + self.comment if self.comment else "")
