# -*- coding: utf-8 -*-

from snes2asm.disassembler import Instruction

# SPC700 instruction sizes (1-3 bytes per instruction)
SPC700InstructionSizes = [
	2, 1, 2, 2, 2, 2, 2, 2, 2, 3, 3, 2, 3, 1, 3, 3, # 0x
	2, 1, 2, 2, 3, 2, 2, 2, 3, 2, 2, 2, 2, 1, 2, 2, # 1x
	1, 1, 2, 2, 2, 2, 2, 2, 2, 3, 3, 2, 3, 1, 3, 3, # 2x
	2, 1, 2, 2, 3, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, # 3x
	1, 1, 2, 2, 2, 2, 2, 2, 2, 3, 3, 2, 3, 1, 3, 3, # 4x
	2, 1, 2, 2, 3, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, # 5x
	1, 1, 2, 2, 2, 2, 2, 2, 2, 3, 3, 2, 3, 1, 3, 3, # 6x
	2, 1, 2, 2, 3, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, # 7x
	2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 3, 2, 3, 2, 2, 1, # 8x
	2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 3, 2, 3, 2, 2, 1, # 9x
	2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 3, 2, 3, 1, 1, 1, # Ax
	2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 3, 2, 3, 1, 1, 1, # Bx
	2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 3, 2, 3, 2, 2, 1, # Cx
	2, 1, 2, 2, 3, 2, 2, 2, 2, 2, 3, 2, 3, 1, 2, 1, # Dx
	2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 3, 2, 3, 1, 2, 1, # Ex
	2, 1, 2, 2, 3, 2, 2, 2, 2, 2, 3, 2, 3, 1, 2, 1, # Fx
]

class SPC700Disassembler:
	"""
	Disassembler for SPC700 audio processor code.
	Generates assembly output from SPC700 machine code.
	"""

	def __init__(self, data, start_addr=0x0000):
		"""
		Initialize the SPC700 disassembler.

		Args:
			data: Binary data containing SPC700 machine code
			start_addr: Starting address for the code (default 0x0000)
		"""
		self.data = data
		self.start_addr = start_addr
		self.pos = 0
		self.labels = {}
		self.op_func = [getattr(self, 'op%02X' % op, self.op_unknown) for op in range(256)]

	def disassemble(self):
		"""
		Disassemble the entire data and return assembly instructions.

		Yields:
			Tuple of (offset, Instruction) for each instruction
		"""
		self.pos = 0
		while self.pos < len(self.data):
			offset = self.pos
			op = self.data[self.pos]

			# Get instruction size and check boundaries
			op_size = SPC700InstructionSizes[op]
			if self.pos + op_size > len(self.data):
				# Incomplete instruction at end of data
				remaining = len(self.data) - self.pos
				hex_bytes = " ".join("%02X" % self.data[self.pos + i] for i in range(remaining))
				ins = self.ins(".db " + ", ".join("$%02X" % self.data[self.pos + i] for i in range(remaining)),
				               comment="Incomplete instruction: %s" % hex_bytes)
				yield (offset, ins)
				break

			# Get instruction handler
			func = self.op_func[op]
			ins = func()

			# Add hex comment
			if op_size == 1:
				ins.comment = "%02X" % op
			elif op_size == 2:
				ins.comment = "%02X %02X" % (op, self.data[self.pos + 1])
			elif op_size == 3:
				ins.comment = "%02X %02X %02X" % (op, self.data[self.pos + 1], self.data[self.pos + 2])

			yield (offset, ins)

			self.pos += op_size

	def ins(self, code, comment=None):
		"""Create an instruction object."""
		return Instruction(code, comment=comment)

	def op_unknown(self):
		"""Handler for unknown/unimplemented opcodes."""
		op = self.data[self.pos]
		return self.ins(".db $%02X" % op, comment="Unknown opcode")

	def pipe8(self):
		"""Read 8-bit immediate value."""
		return self.data[self.pos + 1]

	def pipe16(self):
		"""Read 16-bit immediate value (little-endian)."""
		return self.data[self.pos + 1] | (self.data[self.pos + 2] << 8)

	def pipe8_signed(self):
		"""Read signed 8-bit value for relative branches."""
		val = self.pipe8()
		if val > 127:
			val = val - 256
		return val

	def addr_direct(self):
		"""Direct page address: $XX."""
		return "$%02X" % self.pipe8()

	def addr_direct_x(self):
		"""Direct page indexed by X: $XX+X."""
		return "$%02X+X" % self.pipe8()

	def addr_direct_y(self):
		"""Direct page indexed by Y: $XX+Y."""
		return "$%02X+Y" % self.pipe8()

	def addr_absolute(self):
		"""Absolute address: $XXXX."""
		return "$%04X" % self.pipe16()

	def addr_absolute_x(self):
		"""Absolute indexed by X: $XXXX+X."""
		return "$%04X+X" % self.pipe16()

	def addr_absolute_y(self):
		"""Absolute indexed by Y: $XXXX+Y."""
		return "$%04X+Y" % self.pipe16()

	def addr_indirect_x(self):
		"""Indirect X: ($XX+X)."""
		return "($%02X+X)" % self.pipe8()

	def addr_indirect_y(self):
		"""Indirect Y: ($XX)+Y."""
		return "($%02X)+Y" % self.pipe8()

	def addr_x_indirect(self):
		"""X indirect: (X)."""
		return "(X)"

	def addr_y_indirect(self):
		"""Y indirect: (Y)."""
		return "(Y)"

	def addr_imm8(self):
		"""8-bit immediate: #$XX."""
		return "#$%02X" % self.pipe8()

	def addr_relative(self):
		"""Relative branch offset."""
		offset = self.pipe8_signed()
		target = (self.start_addr + self.pos + 2 + offset) & 0xFFFF
		return "$%04X" % target

	# MOV instructions (0x00-0x0F, scattered throughout)
	def op00(self): return self.ins("nop")

	def op01(self): return self.ins("tcall 0")
	def op11(self): return self.ins("tcall 1")
	def op21(self): return self.ins("tcall 2")
	def op31(self): return self.ins("tcall 3")
	def op41(self): return self.ins("tcall 4")
	def op51(self): return self.ins("tcall 5")
	def op61(self): return self.ins("tcall 6")
	def op71(self): return self.ins("tcall 7")
	def op81(self): return self.ins("tcall 8")
	def op91(self): return self.ins("tcall 9")
	def opA1(self): return self.ins("tcall 10")
	def opB1(self): return self.ins("tcall 11")
	def opC1(self): return self.ins("tcall 12")
	def opD1(self): return self.ins("tcall 13")
	def opE1(self): return self.ins("tcall 14")
	def opF1(self): return self.ins("tcall 15")

	def op02(self): return self.ins("set1 %s.0" % self.addr_direct())
	def op22(self): return self.ins("set1 %s.1" % self.addr_direct())
	def op42(self): return self.ins("set1 %s.2" % self.addr_direct())
	def op62(self): return self.ins("set1 %s.3" % self.addr_direct())
	def op82(self): return self.ins("set1 %s.4" % self.addr_direct())
	def opA2(self): return self.ins("set1 %s.5" % self.addr_direct())
	def opC2(self): return self.ins("set1 %s.6" % self.addr_direct())
	def opE2(self): return self.ins("set1 %s.7" % self.addr_direct())

	def op12(self): return self.ins("clr1 %s.0" % self.addr_direct())
	def op32(self): return self.ins("clr1 %s.1" % self.addr_direct())
	def op52(self): return self.ins("clr1 %s.2" % self.addr_direct())
	def op72(self): return self.ins("clr1 %s.3" % self.addr_direct())
	def op92(self): return self.ins("clr1 %s.4" % self.addr_direct())
	def opB2(self): return self.ins("clr1 %s.5" % self.addr_direct())
	def opD2(self): return self.ins("clr1 %s.6" % self.addr_direct())
	def opF2(self): return self.ins("clr1 %s.7" % self.addr_direct())

	def op03(self):
		dp = self.pipe8()
		rel = self.pipe8_signed()
		target = (self.start_addr + self.pos + 3 + rel) & 0xFFFF
		return self.ins("bbs %s.0,$%04X" % (self.addr_direct(), target))

	def op23(self):
		dp = self.pipe8()
		rel = self.pipe8_signed()
		target = (self.start_addr + self.pos + 3 + rel) & 0xFFFF
		return self.ins("bbs %s.1,$%04X" % (self.addr_direct(), target))

	def op43(self):
		dp = self.pipe8()
		rel = self.pipe8_signed()
		target = (self.start_addr + self.pos + 3 + rel) & 0xFFFF
		return self.ins("bbs %s.2,$%04X" % (self.addr_direct(), target))

	def op63(self):
		dp = self.pipe8()
		rel = self.pipe8_signed()
		target = (self.start_addr + self.pos + 3 + rel) & 0xFFFF
		return self.ins("bbs %s.3,$%04X" % (self.addr_direct(), target))

	def op83(self):
		dp = self.pipe8()
		rel = self.pipe8_signed()
		target = (self.start_addr + self.pos + 3 + rel) & 0xFFFF
		return self.ins("bbs %s.4,$%04X" % (self.addr_direct(), target))

	def opA3(self):
		dp = self.pipe8()
		rel = self.pipe8_signed()
		target = (self.start_addr + self.pos + 3 + rel) & 0xFFFF
		return self.ins("bbs %s.5,$%04X" % (self.addr_direct(), target))

	def opC3(self):
		dp = self.pipe8()
		rel = self.pipe8_signed()
		target = (self.start_addr + self.pos + 3 + rel) & 0xFFFF
		return self.ins("bbs %s.6,$%04X" % (self.addr_direct(), target))

	def opE3(self):
		dp = self.pipe8()
		rel = self.pipe8_signed()
		target = (self.start_addr + self.pos + 3 + rel) & 0xFFFF
		return self.ins("bbs %s.7,$%04X" % (self.addr_direct(), target))

	def op13(self):
		dp = self.pipe8()
		rel = self.pipe8_signed()
		target = (self.start_addr + self.pos + 3 + rel) & 0xFFFF
		return self.ins("bbc %s.0,$%04X" % (self.addr_direct(), target))

	def op33(self):
		dp = self.pipe8()
		rel = self.pipe8_signed()
		target = (self.start_addr + self.pos + 3 + rel) & 0xFFFF
		return self.ins("bbc %s.1,$%04X" % (self.addr_direct(), target))

	def op53(self):
		dp = self.pipe8()
		rel = self.pipe8_signed()
		target = (self.start_addr + self.pos + 3 + rel) & 0xFFFF
		return self.ins("bbc %s.2,$%04X" % (self.addr_direct(), target))

	def op73(self):
		dp = self.pipe8()
		rel = self.pipe8_signed()
		target = (self.start_addr + self.pos + 3 + rel) & 0xFFFF
		return self.ins("bbc %s.3,$%04X" % (self.addr_direct(), target))

	def op93(self):
		dp = self.pipe8()
		rel = self.pipe8_signed()
		target = (self.start_addr + self.pos + 3 + rel) & 0xFFFF
		return self.ins("bbc %s.4,$%04X" % (self.addr_direct(), target))

	def opB3(self):
		dp = self.pipe8()
		rel = self.pipe8_signed()
		target = (self.start_addr + self.pos + 3 + rel) & 0xFFFF
		return self.ins("bbc %s.5,$%04X" % (self.addr_direct(), target))

	def opD3(self):
		dp = self.pipe8()
		rel = self.pipe8_signed()
		target = (self.start_addr + self.pos + 3 + rel) & 0xFFFF
		return self.ins("bbc %s.6,$%04X" % (self.addr_direct(), target))

	def opF3(self):
		dp = self.pipe8()
		rel = self.pipe8_signed()
		target = (self.start_addr + self.pos + 3 + rel) & 0xFFFF
		return self.ins("bbc %s.7,$%04X" % (self.addr_direct(), target))

	def op04(self): return self.ins("or a,%s" % self.addr_direct())
	def op05(self): return self.ins("or a,%s" % self.addr_absolute())
	def op06(self): return self.ins("or a,(X)")
	def op07(self): return self.ins("or a,%s" % self.addr_indirect_x())
	def op08(self): return self.ins("or a,%s" % self.addr_imm8())
	def op09(self):
		dp1 = self.data[self.pos + 1]
		dp2 = self.data[self.pos + 2]
		return self.ins("or $%02X,$%02X" % (dp1, dp2))

	def op0A(self):
		addr = self.pipe16()
		bit = (addr >> 13) & 0x7
		addr = addr & 0x1FFF
		return self.ins("or1 C,$%04X.%d" % (addr, bit))

	def op0B(self): return self.ins("asl %s" % self.addr_direct())
	def op0C(self): return self.ins("asl %s" % self.addr_absolute())
	def op0D(self): return self.ins("push PSW")
	def op0E(self): return self.ins("tset1 %s" % self.addr_absolute())
	def op0F(self): return self.ins("brk")

	def op10(self): return self.ins("bpl %s" % self.addr_relative())

	def op14(self): return self.ins("or a,%s" % self.addr_direct_x())
	def op15(self): return self.ins("or a,%s" % self.addr_absolute_x())
	def op16(self): return self.ins("or a,%s" % self.addr_absolute_y())
	def op17(self): return self.ins("or a,%s" % self.addr_indirect_y())
	def op18(self):
		dp = self.data[self.pos + 1]
		imm = self.data[self.pos + 2]
		return self.ins("or $%02X,#$%02X" % (dp, imm))
	def op19(self): return self.ins("or (X),(Y)")
	def op1A(self): return self.ins("decw %s" % self.addr_direct())
	def op1B(self): return self.ins("asl %s" % self.addr_direct_x())
	def op1C(self): return self.ins("asl A")
	def op1D(self): return self.ins("dec X")
	def op1E(self): return self.ins("cmp X,%s" % self.addr_absolute())
	def op1F(self): return self.ins("jmp [%s+X]" % self.addr_absolute_x())

	def op20(self): return self.ins("clrp")

	def op24(self): return self.ins("and a,%s" % self.addr_direct())
	def op25(self): return self.ins("and a,%s" % self.addr_absolute())
	def op26(self): return self.ins("and a,(X)")
	def op27(self): return self.ins("and a,%s" % self.addr_indirect_x())
	def op28(self): return self.ins("and a,%s" % self.addr_imm8())
	def op29(self):
		dp1 = self.data[self.pos + 1]
		dp2 = self.data[self.pos + 2]
		return self.ins("and $%02X,$%02X" % (dp1, dp2))
	def op2A(self):
		addr = self.pipe16()
		bit = (addr >> 13) & 0x7
		addr = addr & 0x1FFF
		return self.ins("or1 C,!$%04X.%d" % (addr, bit))
	def op2B(self): return self.ins("rol %s" % self.addr_direct())
	def op2C(self): return self.ins("rol %s" % self.addr_absolute())
	def op2D(self): return self.ins("push A")
	def op2E(self): return self.ins("cbne %s,%s" % (self.addr_direct(), self.addr_relative()))
	def op2F(self): return self.ins("bra %s" % self.addr_relative())

	def op30(self): return self.ins("bmi %s" % self.addr_relative())

	def op34(self): return self.ins("and a,%s" % self.addr_direct_x())
	def op35(self): return self.ins("and a,%s" % self.addr_absolute_x())
	def op36(self): return self.ins("and a,%s" % self.addr_absolute_y())
	def op37(self): return self.ins("and a,%s" % self.addr_indirect_y())
	def op38(self):
		dp = self.data[self.pos + 1]
		imm = self.data[self.pos + 2]
		return self.ins("and $%02X,#$%02X" % (dp, imm))
	def op39(self): return self.ins("and (X),(Y)")
	def op3A(self): return self.ins("incw %s" % self.addr_direct())
	def op3B(self): return self.ins("rol %s" % self.addr_direct_x())
	def op3C(self): return self.ins("rol A")
	def op3D(self): return self.ins("inc X")
	def op3E(self): return self.ins("cmp X,%s" % self.addr_direct())
	def op3F(self): return self.ins("call %s" % self.addr_absolute())

	def op40(self): return self.ins("setp")

	def op44(self): return self.ins("eor a,%s" % self.addr_direct())
	def op45(self): return self.ins("eor a,%s" % self.addr_absolute())
	def op46(self): return self.ins("eor a,(X)")
	def op47(self): return self.ins("eor a,%s" % self.addr_indirect_x())
	def op48(self): return self.ins("eor a,%s" % self.addr_imm8())
	def op49(self):
		dp1 = self.data[self.pos + 1]
		dp2 = self.data[self.pos + 2]
		return self.ins("eor $%02X,$%02X" % (dp1, dp2))
	def op4A(self):
		addr = self.pipe16()
		bit = (addr >> 13) & 0x7
		addr = addr & 0x1FFF
		return self.ins("and1 C,$%04X.%d" % (addr, bit))
	def op4B(self): return self.ins("lsr %s" % self.addr_direct())
	def op4C(self): return self.ins("lsr %s" % self.addr_absolute())
	def op4D(self): return self.ins("push X")
	def op4E(self): return self.ins("tclr1 %s" % self.addr_absolute())
	def op4F(self): return self.ins("pcall $%02X" % self.pipe8())

	def op50(self): return self.ins("bvc %s" % self.addr_relative())

	def op54(self): return self.ins("eor a,%s" % self.addr_direct_x())
	def op55(self): return self.ins("eor a,%s" % self.addr_absolute_x())
	def op56(self): return self.ins("eor a,%s" % self.addr_absolute_y())
	def op57(self): return self.ins("eor a,%s" % self.addr_indirect_y())
	def op58(self):
		dp = self.data[self.pos + 1]
		imm = self.data[self.pos + 2]
		return self.ins("eor $%02X,#$%02X" % (dp, imm))
	def op59(self): return self.ins("eor (X),(Y)")
	def op5A(self): return self.ins("cmpw YA,%s" % self.addr_direct())
	def op5B(self): return self.ins("lsr %s" % self.addr_direct_x())
	def op5C(self): return self.ins("lsr A")
	def op5D(self): return self.ins("mov X,A")
	def op5E(self): return self.ins("cmp Y,%s" % self.addr_absolute())
	def op5F(self): return self.ins("jmp %s" % self.addr_absolute())

	def op60(self): return self.ins("clrc")

	def op64(self): return self.ins("cmp a,%s" % self.addr_direct())
	def op65(self): return self.ins("cmp a,%s" % self.addr_absolute())
	def op66(self): return self.ins("cmp a,(X)")
	def op67(self): return self.ins("cmp a,%s" % self.addr_indirect_x())
	def op68(self): return self.ins("cmp a,%s" % self.addr_imm8())
	def op69(self):
		dp1 = self.data[self.pos + 1]
		dp2 = self.data[self.pos + 2]
		return self.ins("cmp $%02X,$%02X" % (dp1, dp2))
	def op6A(self):
		addr = self.pipe16()
		bit = (addr >> 13) & 0x7
		addr = addr & 0x1FFF
		return self.ins("and1 C,!$%04X.%d" % (addr, bit))
	def op6B(self): return self.ins("ror %s" % self.addr_direct())
	def op6C(self): return self.ins("ror %s" % self.addr_absolute())
	def op6D(self): return self.ins("push Y")
	def op6E(self):
		dp = self.data[self.pos + 1]
		rel = self.pipe8_signed()
		target = (self.start_addr + self.pos + 3 + rel) & 0xFFFF
		return self.ins("dbnz $%02X,$%04X" % (dp, target))
	def op6F(self): return self.ins("ret")

	def op70(self): return self.ins("bvs %s" % self.addr_relative())

	def op74(self): return self.ins("cmp a,%s" % self.addr_direct_x())
	def op75(self): return self.ins("cmp a,%s" % self.addr_absolute_x())
	def op76(self): return self.ins("cmp a,%s" % self.addr_absolute_y())
	def op77(self): return self.ins("cmp a,%s" % self.addr_indirect_y())
	def op78(self):
		dp = self.data[self.pos + 1]
		imm = self.data[self.pos + 2]
		return self.ins("cmp $%02X,#$%02X" % (dp, imm))
	def op79(self): return self.ins("cmp (X),(Y)")
	def op7A(self): return self.ins("addw YA,%s" % self.addr_direct())
	def op7B(self): return self.ins("ror %s" % self.addr_direct_x())
	def op7C(self): return self.ins("ror A")
	def op7D(self): return self.ins("mov A,X")
	def op7E(self): return self.ins("cmp Y,%s" % self.addr_direct())
	def op7F(self): return self.ins("reti")

	def op80(self): return self.ins("setc")

	def op84(self): return self.ins("adc a,%s" % self.addr_direct())
	def op85(self): return self.ins("adc a,%s" % self.addr_absolute())
	def op86(self): return self.ins("adc a,(X)")
	def op87(self): return self.ins("adc a,%s" % self.addr_indirect_x())
	def op88(self): return self.ins("adc a,%s" % self.addr_imm8())
	def op89(self):
		dp1 = self.data[self.pos + 1]
		dp2 = self.data[self.pos + 2]
		return self.ins("adc $%02X,$%02X" % (dp1, dp2))
	def op8A(self):
		addr = self.pipe16()
		bit = (addr >> 13) & 0x7
		addr = addr & 0x1FFF
		return self.ins("eor1 C,$%04X.%d" % (addr, bit))
	def op8B(self): return self.ins("dec %s" % self.addr_direct())
	def op8C(self): return self.ins("dec %s" % self.addr_absolute())
	def op8D(self): return self.ins("mov Y,%s" % self.addr_imm8())
	def op8E(self): return self.ins("pop PSW")
	def op8F(self):
		dp = self.data[self.pos + 1]
		imm = self.data[self.pos + 2]
		return self.ins("mov $%02X,#$%02X" % (dp, imm))

	def op90(self): return self.ins("bcc %s" % self.addr_relative())

	def op94(self): return self.ins("adc a,%s" % self.addr_direct_x())
	def op95(self): return self.ins("adc a,%s" % self.addr_absolute_x())
	def op96(self): return self.ins("adc a,%s" % self.addr_absolute_y())
	def op97(self): return self.ins("adc a,%s" % self.addr_indirect_y())
	def op98(self):
		dp = self.data[self.pos + 1]
		imm = self.data[self.pos + 2]
		return self.ins("adc $%02X,#$%02X" % (dp, imm))
	def op99(self): return self.ins("adc (X),(Y)")
	def op9A(self): return self.ins("subw YA,%s" % self.addr_direct())
	def op9B(self): return self.ins("dec %s" % self.addr_direct_x())
	def op9C(self): return self.ins("dec A")
	def op9D(self): return self.ins("mov X,SP")
	def op9E(self): return self.ins("div YA,X")
	def op9F(self): return self.ins("xcn A")

	def opA0(self): return self.ins("ei")

	def opA4(self): return self.ins("sbc a,%s" % self.addr_direct())
	def opA5(self): return self.ins("sbc a,%s" % self.addr_absolute())
	def opA6(self): return self.ins("sbc a,(X)")
	def opA7(self): return self.ins("sbc a,%s" % self.addr_indirect_x())
	def opA8(self): return self.ins("sbc a,%s" % self.addr_imm8())
	def opA9(self):
		dp1 = self.data[self.pos + 1]
		dp2 = self.data[self.pos + 2]
		return self.ins("sbc $%02X,$%02X" % (dp1, dp2))
	def opAA(self):
		addr = self.pipe16()
		bit = (addr >> 13) & 0x7
		addr = addr & 0x1FFF
		return self.ins("mov1 C,$%04X.%d" % (addr, bit))
	def opAB(self): return self.ins("inc %s" % self.addr_direct())
	def opAC(self): return self.ins("inc %s" % self.addr_absolute())
	def opAD(self): return self.ins("cmp Y,%s" % self.addr_imm8())
	def opAE(self): return self.ins("pop A")
	def opAF(self): return self.ins("mov (X)+,A")

	def opB0(self): return self.ins("bcs %s" % self.addr_relative())

	def opB4(self): return self.ins("sbc a,%s" % self.addr_direct_x())
	def opB5(self): return self.ins("sbc a,%s" % self.addr_absolute_x())
	def opB6(self): return self.ins("sbc a,%s" % self.addr_absolute_y())
	def opB7(self): return self.ins("sbc a,%s" % self.addr_indirect_y())
	def opB8(self):
		dp = self.data[self.pos + 1]
		imm = self.data[self.pos + 2]
		return self.ins("sbc $%02X,#$%02X" % (dp, imm))
	def opB9(self): return self.ins("sbc (X),(Y)")
	def opBA(self): return self.ins("movw YA,%s" % self.addr_direct())
	def opBB(self): return self.ins("inc %s" % self.addr_direct_x())
	def opBC(self): return self.ins("inc A")
	def opBD(self): return self.ins("mov SP,X")
	def opBE(self): return self.ins("das A")
	def opBF(self): return self.ins("mov A,(X)+")

	def opC0(self): return self.ins("di")

	def opC4(self): return self.ins("mov %s,A" % self.addr_direct())
	def opC5(self): return self.ins("mov %s,A" % self.addr_absolute())
	def opC6(self): return self.ins("mov (X),A")
	def opC7(self): return self.ins("mov %s,A" % self.addr_indirect_x())
	def opC8(self): return self.ins("cmp X,%s" % self.addr_imm8())
	def opC9(self): return self.ins("mov %s,X" % self.addr_absolute())
	def opCA(self):
		addr = self.pipe16()
		bit = (addr >> 13) & 0x7
		addr = addr & 0x1FFF
		return self.ins("mov1 $%04X.%d,C" % (addr, bit))
	def opCB(self): return self.ins("mov %s,Y" % self.addr_direct())
	def opCC(self): return self.ins("mov %s,Y" % self.addr_absolute())
	def opCD(self): return self.ins("mov X,%s" % self.addr_imm8())
	def opCE(self): return self.ins("pop X")
	def opCF(self): return self.ins("mul YA")

	def opD0(self): return self.ins("bne %s" % self.addr_relative())

	def opD4(self): return self.ins("mov %s,A" % self.addr_direct_x())
	def opD5(self): return self.ins("mov %s,A" % self.addr_absolute_x())
	def opD6(self): return self.ins("mov %s,A" % self.addr_absolute_y())
	def opD7(self): return self.ins("mov %s,A" % self.addr_indirect_y())
	def opD8(self): return self.ins("mov %s,X" % self.addr_direct())
	def opD9(self): return self.ins("mov %s,Y" % self.addr_direct_x())
	def opDA(self): return self.ins("movw %s,YA" % self.addr_direct())
	def opDB(self): return self.ins("mov %s,Y" % self.addr_direct_x())
	def opDC(self): return self.ins("dec Y")
	def opDD(self): return self.ins("mov A,Y")
	def opDE(self):
		dp = self.data[self.pos + 1]
		rel = self.pipe8_signed()
		target = (self.start_addr + self.pos + 3 + rel) & 0xFFFF
		return self.ins("cbne %s,$%04X" % (self.addr_direct_x(), target))
	def opDF(self): return self.ins("daa A")

	def opE0(self): return self.ins("clrv")

	def opE4(self): return self.ins("mov a,%s" % self.addr_direct())
	def opE5(self): return self.ins("mov a,%s" % self.addr_absolute())
	def opE6(self): return self.ins("mov a,(X)")
	def opE7(self): return self.ins("mov a,%s" % self.addr_indirect_x())
	def opE8(self): return self.ins("mov a,%s" % self.addr_imm8())
	def opE9(self): return self.ins("mov X,%s" % self.addr_absolute())
	def opEA(self):
		addr = self.pipe16()
		bit = (addr >> 13) & 0x7
		addr = addr & 0x1FFF
		return self.ins("not1 $%04X.%d" % (addr, bit))
	def opEB(self): return self.ins("mov Y,%s" % self.addr_direct())
	def opEC(self): return self.ins("mov Y,%s" % self.addr_absolute())
	def opED(self): return self.ins("notc")
	def opEE(self): return self.ins("pop Y")
	def opEF(self): return self.ins("sleep")

	def opF0(self): return self.ins("beq %s" % self.addr_relative())

	def opF4(self): return self.ins("mov a,%s" % self.addr_direct_x())
	def opF5(self): return self.ins("mov a,%s" % self.addr_absolute_x())
	def opF6(self): return self.ins("mov a,%s" % self.addr_absolute_y())
	def opF7(self): return self.ins("mov a,%s" % self.addr_indirect_y())
	def opF8(self): return self.ins("mov X,%s" % self.addr_direct())
	def opF9(self): return self.ins("mov X,%s" % self.addr_direct_y())
	def opFA(self):
		dp1 = self.data[self.pos + 1]
		dp2 = self.data[self.pos + 2]
		return self.ins("mov $%02X,$%02X" % (dp1, dp2))
	def opFB(self): return self.ins("mov Y,%s" % self.addr_direct_x())
	def opFC(self): return self.ins("inc Y")
	def opFD(self): return self.ins("mov Y,A")
	def opFE(self):
		rel = self.pipe8_signed()
		target = (self.start_addr + self.pos + 2 + rel) & 0xFFFF
		return self.ins("dbnz Y,$%04X" % target)
	def opFF(self): return self.ins("stop")
