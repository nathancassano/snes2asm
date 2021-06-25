
import snes2asm
from collections import OrderedDict
import io

from snes2asm.cartridge import Cartridge

InstructionSizes = [
	2, 3, 1, 1, 3, 3, 3, 1, 2, 3, 2, 1, 4, 4, 4, 1,
	3, 3, 1, 1, 3, 3, 3, 1, 2, 4, 2, 1, 4, 4, 4, 1,
	4, 3, 1, 1, 3, 3, 3, 1, 2, 3, 2, 1, 4, 4, 4, 1,
	3, 3, 1, 1, 3, 3, 3, 1, 2, 4, 2, 1, 4, 4, 4, 1,
	2, 3, 1, 1, 3, 3, 3, 1, 2, 3, 2, 1, 4, 4, 4, 1,
	3, 3, 1, 1, 3, 3, 3, 1, 2, 4, 2, 1, 4, 4, 4, 1,
	2, 3, 1, 1, 3, 3, 3, 1, 2, 3, 2, 1, 4, 4, 4, 1,
	3, 3, 1, 1, 3, 3, 3, 1, 2, 4, 2, 1, 4, 4, 4, 1,
	3, 3, 1, 1, 3, 3, 3, 1, 2, 1, 2, 1, 4, 4, 4, 1,
	3, 3, 1, 1, 3, 3, 3, 1, 2, 4, 2, 1, 1, 4, 1, 1,
	3, 3, 3, 1, 3, 3, 3, 1, 2, 3, 2, 1, 4, 4, 4, 1,
	3, 3, 1, 1, 3, 3, 3, 1, 2, 4, 2, 1, 4, 4, 4, 1,
	3, 3, 1, 1, 3, 3, 3, 1, 2, 3, 2, 1, 4, 4, 4, 1,
	3, 3, 1, 1, 3, 3, 3, 1, 2, 4, 2, 1, 4, 4, 4, 1,
	3, 3, 1, 1, 3, 3, 3, 1, 2, 3, 2, 1, 4, 4, 4, 1,
	3, 3, 1, 1, 3, 3, 3, 1, 2, 4, 2, 1, 4, 4, 4, 1
]

class Disassembler:

	def __init__(self, cart):
		self.cart = cart
		self.pos = 0
		self.flags = 0
		self.labels = set()
		self.instr = OrderedDict()

	def run(self):

		size = len(self.cart.data)

		while self.pos < size:
			op = self.cart[self.pos]
			op_size = self.opSize(op)

			if (self.cart.address(pos) & 0xFFFF) + op_size > 0xFFFF:
				print("Opcode %02X overrunning bank boundry at %X. Skipping." % (op, self.pos))
				self.ins(".byte $%02X" % op)
				self.pos = self.pos + 1
				continue
				

			func = getattr(self, 'op%02X' % op)
			if not func:
				print("Unhandled opcode: %02X at %X" % (op, self.pos))
				self.ins(".byte $%02X" % op)
				self.pos = self.pos + 1
				continue
			func()
			self.pos = self.pos + op_size

	def acc16(self):
		return self.flags & 0x20 == 0

	def ind16(self):
		return self.flags & 0x10 == 0

	def set_label(self, address):
		self.labels.add(address)	

	# Append instruction
	def ins(self, code, preamble=None, comment=None):
		self.instr[self.cart.address(self.pos)] = Instruction(code,preamble,comment)

	def opSize(op):
		size = InstructionSizes[op]
		if self.acc16() and op in [0x09,0x69, 0x29, 0x89, 0xC9, 0x49, 0xE9, 0xA9]:
			size = size + 1
		if self.ind16() and op in [0xE0, 0xC0, 0xA2]:
			size = size + 1
		return size

	def op01(self):
		self.ins("ora" + self.dir_page_ind_indir_x())

	# ADC
	def op69(self):
		self.ins("adc" + self.immediate())

	def op6D(self):
		self.ins("adc" + self.abs())

	def op6F(self):
		self.ins("adc" + self.abs_long())

	def op65(self):
		self.ins("adc" + self.dir_page())

	def op72(self):
		self.ins("adc" + self.dir_page_indir())

	def op67(self):
		self.ins("adc" + self.dir_page_indir_long())

	def op7D(self):
		self.ins("adc" + self.abs_ind_x())

	def op7F(self):
		self.ins("adc" + self.abs_long_ind_x())

	def op79(self):
		self.ins("adc" + self.abs_ind_y())

	def op75(self):
		self.ins("adc" + self.dir_page_ind_x())

	def op61(self):
		self.ins("adc" + self.dir_page_ind_indir_x())

	def op71(self):
		self.ins("adc" + self.dir_page_ind_indir_y())

	def op77(self):
		self.ins("adc" + self.dir_page_indir_long_y())

	def op63(self):
		self.ins("adc" + self.stack_rel())

	def op73(self):
		self.ins("adc" + self.stack_rel_indir_y())

	# AND
	def op29(self):
		self.ins("and" + self.immediate())

	def op2D(self):
		self.ins("and" + self.abs())

	def op2F(self):
		self.ins("and" + self.abs_long())

	def op25(self):
		self.ins("and" + self.dir_page())

	def op32(self):
		self.ins("and" + self.dir_page_indir())

	def op27(self):
		self.ins("and" + self.dir_page_indir_long())

	def op3D(self):
		self.ins("and" + self.abs_ind_x())

	def op3F(self):
		self.ins("and" + self.abs_long_ind_x())

	def op39(self):
		self.ins("and" + self.abs_ind_y())

	def op35(self):
		self.ins("and" + self.dir_page_ind_x())

	def op21(self):
		self.ins("and" + self.dir_page_ind_indir_x())

	def op31(self):
		self.ins("and" + self.dir_page_ind_indir_y())

	def op37(self):
		self.ins("and" + self.dir_page_indir_long_y())

	def op23(self):
		self.ins("and" + self.stack_rel())

	def op33(self):
		self.ins("and" + self.stack_rel_indir_y())

	# ASL
	def op0A(self):
		self.ins("asl")

	def op0E(self):
		self.ins("asl" + self.abs())

	def op06(self):
		self.ins("asl" + self.dir_page())

	def op1E(self):
		self.ins("asl" + self.abs_ind_x())

	def op16(self):
		self.ins("asl" + self.dir_page_ind_x())

	# BCC
	def op90(self):
		self.ins("bcc")
 
 	# BCS
	def opB0(self):
		self.ins("bcs")
 
 	# BEQ
	def opF0(self):
		self.ins("beq")
 
 	# BNE
	def opD0(self):
		self.ins("bne")
 
 	# BMI
	def op30(self):
		self.ins("bmi")
 
 	# BPL
	def op10(self):
		self.ins("bpl")
 
 	# BVC
	def op50(self):
		self.ins("bvc")
 
 	# BVS
	def op70(self):
		self.ins("bvs")
 
 	# BRA
	def op80(self):
		self.ins("bra")
 
 	# BRL
	def op82(self):
		self.ins("brl")

	# BIT
	def op89(self):
		self.ins("bit" + self.immediate())

	def op2C(self):
		self.ins("bit" + self.abs())

	def op24(self):
		self.ins("bit" + self.dir_page())

	def op3C(self):
		self.ins("bit" + self.abs_ind_x())

	def op34(self):
		self.ins("bit" + self.dir_page_ind_x())
 
 	# BRK
	def op00(self):
		self.ins("brk" + self.stack_interrupt())
 
 	# CLC
	def op18(self):
		self.ins("clc")
 
 	# CLD
	def opD8(self):
		self.ins("cld")
 
 	# CLI
	def op58(self):
		self.ins("cli")
 
 	# CLV
	def opB8(self):
		self.ins("clv")
 
 	# SEC
	def op38(self):
		self.ins("sec")
 
 	# SED
	def opF8(self):
		self.ins("sed")
 
 	# SEI
	def op78(self):
		self.ins("sei")

	# CMP
	def opC9(self):
		self.ins("cmp" + self.immediate())

	def opCD(self):
		self.ins("cmp" + self.abs())

	def opCF(self):
		self.ins("cmp" + self.abs_long())

	def opC5(self):
		self.ins("cmp" + self.dir_page())

	def opD2(self):
		self.ins("cmp" + self.dir_page_indir())

	def opC7(self):
		self.ins("cmp" + self.dir_page_indir_long())

	def opDD(self):
		self.ins("cmp" + self.abs_ind_x())

	def opDF(self):
		self.ins("cmp" + self.abs_long_ind_x())

	def opD9(self):
		self.ins("cmp" + self.abs_ind_y())

	def opD5(self):
		self.ins("cmp" + self.dir_page_ind_x())

	def opC1(self):
		self.ins("cmp" + self.dir_page_ind_indir_x())

	def opD1(self):
		self.ins("cmp" + self.dir_page_indir_y())

	def opD7(self):
		self.ins("cmp" + self.dir_page_indir_long_y())

	def opC3(self):
		self.ins("cmp" + self.stack_rel())

	def opD3(self):
		self.ins("cmp" + self.stack_rel_indir_y())

	# COP
	def opD3(self):
		self.ins("cop" + self.stack_interrupt())

	# CPX
	def opE0(self):
		self.ins("cpx" + self.immediate_ind())

	def opEC(self):
		self.ins("cpx" + self.abs())

	def opEC(self):
		self.ins("cpx" + self.dir_page())

	# CPY
	def opC0(self):
		self.ins("cpy" + self.immediate_ind())

	def opCC(self):
		self.ins("cpy" + self.abs())

	def opC4(self):
		self.ins("cpy" + self.dir_page())

	# DEC
	def op3A(self):
		self.ins("dec A")

	def opCE(self):
		self.ins("dec" + self.abs())

	def opC6(self):
		self.ins("dec" + self.dir_page())

	def opDE(self):
		self.ins("dec" + self.abs_ind_x())

	def opD6(self):
		self.ins("dec" + self.dir_page_ind_x())

	# DEX
	def opCA(self):
		self.ins("dex")

	# DEY
	def op88(self):
		self.ins("dey")

	# EOR
	def op49(self):
		self.ins("eor" + self.immediate())

	def op4D(self):
		self.ins("eor" + self.abs())

	def op4F(self):
		self.ins("eor" + self.abs_long())

	def op45(self):
		self.ins("eor" + self.dir_page())

	def op52(self):
		self.ins("eor" + self.dir_page_indir())

	def op47(self):
		self.ins("eor" + self.dir_page_indir_long())

	def op5D(self):
		self.ins("eor" + self.abs_ind_x())

	def op5F(self):
		self.ins("eor" + self.abs_long_ind_x())

	def op59(self):
		self.ins("eor" + self.abs_ind_y())

	def op55(self):
		self.ins("eor" + self.dir_page_ind_x())

	def op41(self):
		self.ins("eor" + self.dir_page_ind_indir_x())

	def op51(self):
		self.ins("eor" + self.dir_page_indir_y())

	def op57(self):
		self.ins("eor" + self.dir_page_indir_long_y())

	def op43(self):
		self.ins("eor" + self.stack_rel())

	def op53(self):
		self.ins("eor" + self.stack_rel_indir_y())

	# INC
	def op1A(self):
		self.ins("inc A")

	def opEE(self):
		self.ins("inc" + self.abs())

	def opE6(self):
		self.ins("inc" + self.dir_page())

	def opFE(self):
		self.ins("inc" + self.abs_ind_x())

	def opF6(self):
		self.ins("inc" + self.dir_page_ind_x())

	# INX
	def opE8(self):
		self.ins("inx")

	# INY
	def opC8(self):
		self.ins("inc A")

	# JMP
	def op4C(self):
		self.ins("jmp" + self.abs())

	def op6C(self):
		self.ins("jmp" + self.abs_indir())

	def op7C(self):
		self.ins("jmp" + self.abs_ind_indir())

	def op5C(self):
		self.ins("jmp" + self.abs_long())

	def opDC(self):
		self.ins("jmp" + self.abs_indir_long())

	# JSR
	def op22(self):
		self.ins("jsr" + self.abs_long())

	def op20(self):
		self.ins("jsr" + self.abs())

	def opFC(self):
		self.ins("jsr" + self.abs_ind_x())

	# LDA
	def opA9(self):
		self.ins("lda" + self.immediate())

	def opAD(self):
		self.ins("lda" + self.abs())

	def opAF(self):
		self.ins("lda" + self.abs_long())

	def opA5(self):
		self.ins("lda" + self.dir_page())

	def opB2(self):
		self.ins("lda" + self.dir_page_indir())

	def opA7(self):
		self.ins("lda" + self.dir_page_indir_long())

	def opBD(self):
		self.ins("lda" + self.abs_ind_x())

	def opBF(self):
		self.ins("lda" + self.abs_long_ind_x())

	def opB9(self):
		self.ins("lda" + self.abs_ind_y())

	def opB5(self):
		self.ins("lda" + self.dir_page_ind_x())

	def opA1(self):
		self.ins("lda" + self.dir_page_ind_indir_x())

	def opB1(self):
		self.ins("lda" + self.dir_page_indir_y())

	def opB7(self):
		self.ins("lda" + self.dir_page_indir_long_y())

	def opA3(self):
		self.ins("lda" + self.stack_rel())

	def opB3(self):
		self.ins("lda" + self.stack_rel_indir_y())

	# LDX
	def opA2(self):
		self.ins("ldx" + self.immediate_ind())

	def opAE(self):
		self.ins("ldx" + self.abs())

	def opA6(self):
		self.ins("ldx" + self.dir_page())

	def opBE(self):
		self.ins("ldx" + self.abs_ind_y())

	def opB6(self):
		self.ins("ldx" + self.dir_page_ind_y())

	# LDY
	def opA0(self):
		self.ins("ldy" + self.immidate_ind())

	def opAC(self):
		self.ins("ldy" + self.abs())

	def opA4(self):
		self.ins("ldy" + self.dir_page())

	def opBC(self):
		self.ins("ldy" + self.abs_ind_x())

	def opB4(self):
		self.ins("ldy" + self.dir_page_ind_y())

	# LSR
	def op4A(self):
		self.ins("lsr A")

	def op4E(self):
		self.ins("lsr" + self.abs())

	def op46(self):
		self.ins("lsr" + self.dir_page())

	def op5E(self):
		self.ins("lsr" + self.abs_ind_x())

	def op56(self):
		self.ins("lsr" + self.dir_page_ind_x())

	# MVN
	def op54(self):
		self.ins("mvn" + self.block_move())

	# MVP
	def op44(self):
		self.ins("mvp" + self.block_move())

	# NOP
	def opEA(self):
		self.ins("nop")

	# ORA
	def op09(self):
		self.ins("ora" + self.immediate())

	def op0D(self):
		self.ins("ora" + self.abs())

	def op0F(self):
		self.ins("ora" + self.abs_long())

	def op05(self):
		self.ins("ora" + self.dir_page())

	def op12(self):
		self.ins("ora" + self.dir_page_indir())

	def op07(self):
		self.ins("ora" + self.dir_page_indir_long())

	def op1D(self):
		self.ins("ora" + self.abs_ind_x())

	def op1F(self):
		self.ins("ora" + self.abs_long_ind_x())

	def op19(self):
		self.ins("ora" + self.abs_ind_y())

	def op15(self):
		self.ins("ora" + self.dir_page_ind_x())

	def op01(self):
		self.ins("ora" + self.dir_page_ind_indir_x())

	def op11(self):
		self.ins("ora" + self.dir_page_indir_y())

	def op17(self):
		self.ins("ora" + self.dir_page_indir_long_y())

	def op03(self):
		self.ins("ora" + self.stack_rel())

	def op13(self):
		self.ins("ora" + self.stack_rel_indir_y())

 	# PEA
	def opF4(self):
		self.ins("pea" + self.abs())
 
 	# PEI
	def opD4(self):
		self.ins("pei" + self.dir_page_indir())
 
 	# PER
	def op62(self):
		self.ins("per" + self.pc_rel_long())
 
 	# PHA
	def op48(self):
		self.ins("pha")
 
 	# PHP
	def op08(self):
		self.ins("php")
 
 	# PHX
	def opDA(self):
		self.ins("phx")
 
 	# PHY
	def op5A(self):
		self.ins("phy")
 
 	# PLA
	def op68(self):
		self.ins("pla")
 
 	# PLP
	def op28(self):
		self.ins("plp")
 
 	# PLX
	def opFA(self):
		self.ins("plx")
 
 	# PLY
	def op7A(self):
		self.ins("ply")
 
 	# PHB
	def op8B(self):
		self.ins("phb")
 
 	# PHD
	def op0B(self):
		self.ins("phd")
 
 	# PHK
	def op4B(self):
		self.ins("phk")
 
 	# PLB
	def opAB(self):
		self.ins("plb")
 
 	# PLD
	def op2B(self):
		self.ins("pld")

	# REP
	def opC2(self):
		val = self.pipe8()
		self.flags = self.flags & (~val)
		pre = None
		if val & 0x20:
			pre = ".ACCUM16"
		if val & 0x10:
			pre = "" if pre == None else pre + "\n"
			pre = pre + ".INDEX16"
		self.ins("rep", " #$%02X" % self.pipe8(), pre )

	# SEP
	def opE2(self):
		val = self.pipe8()
		self.flags = self.flags & val
		pre = None
		if val & 0x20:
			pre = ".ACCUM8"
		if val & 0x10:
			pre = "" if pre == None else pre + "\n"
			pre = pre + ".INDEX8"
		self.ins("sep", " #$%02X" % self.pipe8(), pre )

	# ROL
	def op2A(self):
		self.ins("rol A")

	def op2E(self):
		self.ins("rol" + self.abs())

	def op26(self):
		self.ins("rol" + self.dir_page())

	def op3E(self):
		self.ins("rol" + self.abs_ind_x())

	def op36(self):
		self.ins("rol" + self.dir_page_ind_x())

	# ROR
	def op6A(self):
		self.ins("ror A")

	def op6E(self):
		self.ins("ror" + self.abs())

	def op66(self):
		self.ins("ror" + self.dir_page())

	def op7E(self):
		self.ins("ror" + self.abs_ind_x())

	def op76(self):
		self.ins("ror" + self.dir_page_ind_x())

	# RTI
	def op40(self):
		self.ins("rti")

	# RTL
	def op6B(self):
		self.ins("rtl")

	# RTS
	def op60(self):
		self.ins("rts")

	# SBC
	def opE9(self):
		self.ins("sbc" + self.immediate())

	def opED(self):
		self.ins("sbc" + self.abs())

	def opEF(self):
		self.ins("sbc" + self.abs_long())

	def opE5(self):
		self.ins("sbc" + self.dir_page())

	def opF2(self):
		self.ins("sbc" + self.dir_page_indir())

	def opE7(self):
		self.ins("sbc" + self.dir_page_indir_long())

	def opFD(self):
		self.ins("sbc" + self.abs_ind_x())

	def opFF(self):
		self.ins("sbc" + self.abs_long_ind_x())

	def opF9(self):
		self.ins("sbc" + self.abs_ind_y())

	def opF5(self):
		self.ins("sbc" + self.dir_page_ind_x())

	def opE1(self):
		self.ins("sbc" + self.dir_page_ind_indir_x())

	def opF1(self):
		self.ins("sbc" + self.dir_page_ind_indir_y())

	def opF7(self):
		self.ins("sbc" + self.dir_page_indir_long_y())

	def opE3(self):
		self.ins("sbc" + self.stack_rel())

	def opF3(self):
		self.ins("sbc" + self.stack_rel_indir_y())

	# STA
	def op8D(self):
		self.ins("sta" + self.abs())

	def op8F(self):
		self.ins("sta" + self.abs_long())

	def op85(self):
		self.ins("sta" + self.dir_page())

	def op92(self):
		self.ins("sta" + self.dir_page_indir())

	def op87(self):
		self.ins("sta" + self.dir_page_indir_long())

	def op9D(self):
		self.ins("sta" + self.abs_ind_x())

	def op9F(self):
		self.ins("sta" + self.abs_long_ind_x())

	def op99(self):
		self.ins("sta" + self.abs_ind_y())

	def op95(self):
		self.ins("sta" + self.dir_page_ind_x())

	def op81(self):
		self.ins("sta" + self.dir_page_ind_indir_x())

	def op91(self):
		self.ins("sta" + self.dir_page_indir_ind_y())

	def op97(self):
		self.ins("sta" + self.dir_page_indir_long_y())

	def op83(self):
		self.ins("sta" + self.stack_rel())

	def op93(self):
		self.ins("sta" + self.stack_rel_indir_y())

	# STP
	def opDB(self):
		self.ins("stp")

	# STX
	def op8E(self):
		self.ins("stx" + self.abs())

	def op86(self):
		self.ins("stx" + self.dir_page())

	def op96(self):
		self.ins("stx" + self.dir_page_ind_y())

	# STY
	def op8C(self):
		self.ins("sty" + self.abs())

	def op84(self):
		self.ins("sty" + self.dir_page())

	def op94(self):
		self.ins("sty" + self.dir_page_ind_x())

	# STZ
	def op9C(self):
		self.ins("stz" + self.abs())

	def op64(self):
		self.ins("stz" + self.dir_page())

	def op9E(self):
		self.ins("stz" + self.abs_ind_x())

	def op74(self):
		self.ins("stz" + self.dir_page_ind_x())

 	# TAX
	def opAA(self):
		self.ins("tax")
 
 	# TAY
	def opA8(self):
		self.ins("tay")
 
 	# TXA
	def op8A(self):
		self.ins("txa")
 
 	# TYA
	def op98(self):
		self.ins("tya")
 
 	# TSX
	def opBA(self):
		self.ins("tsx")
 
 	# TXS
	def op9A(self):
		self.ins("txs")
 
 	# TXY
	def op9B(self):
		self.ins("txy")
 
 	# TYX
	def opBB(self):
		self.ins("tyx")
 
 	# TCD
	def op5B(self):
		self.ins("tcd")
 
 	# TDC
	def op7B(self):
		self.ins("tdc")

 	# TCS
	def op1B(self):
		self.ins("tcs")
 
 	# TSC
	def op3B(self):
		self.ins("tsc")
 
 	# TRB
	def op1C(self):
		self.ins("trb" + self.abs())

	def op14(self):
		self.ins("trb" + self.dir_page())
 
 	# TSB
	def op0C(self):
		self.ins("tsb" + self.abs())

	def op04(self):
		self.ins("tsb" + self.dir_page())
 
 	# WAI
	def opCB(self):
		self.ins("wai")
 
 	# WDM
	def op42(self):
		self.ins("wdm" + " #$%02X" % self.pipe8())
 
 	# XBA
	def opEB(self):
		self.ins("xba")
 
 	# XCE
	def opFB(self):
		self.ins("xce")

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
		return " $%0^X" % self.pipe24()
	
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
		return " ($%02X,Y)" % self.pipe8()

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

	def pc_rel_long(self):
		val = self.pipe16()
		if val > 32767:
			val = val - 65536
		addr = (self.pos + 3 + val) & 0xFFFF
		return " $%04lX" % addr

	def pipe8(self):
		self.cart[self.pos+1]

	def pipe16(self):
		return self.cart[self.pos+1] | (self.cart[self.pos+2] << 8)

	def pipe24(self):
		return self.cart[self.pos+1] | (self.cart[self.pos+2] << 8) | (self.cart[self.pos+3] << 16)


	def output(path):
		pass


class Instruction:
	def __init__(self, code, preamble=None, comment=None):
		self.code = code
		self.comment = comment
		self.preamble = preamble

	def __str__(self):
		return (self.preamble + "\n" if self.preamble else "") + "\t" + self.code + ( "  " + self.comment if comment else "")
