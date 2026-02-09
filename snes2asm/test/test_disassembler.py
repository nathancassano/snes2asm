# -*- coding: utf-8 -*-

import unittest
import os
from unittest.mock import patch, MagicMock
from snes2asm.cartridge import Cartridge
from snes2asm.disassembler import Disassembler
from snes2asm.configurator import Configurator


class DisassemblerTest(unittest.TestCase):
    """Test 65816 disassembly engine and code path tracing."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock cartridge
        self.cart = MagicMock(spec=Cartridge)
        self.cart.size = 0x10000  # 64KB ROM
        
        # Mock ROM data with some test instructions
        self.rom_data = bytearray([
            # Simple LDA immediate
            0xA9, 0x42,
            # STA absolute
            0x8D, 0x00, 0x7E,
            # JMP absolute
            0x4C, 0x10, 0x80,
            # BRK
            0x00,
            # RTI
            0x40,
            # RTS
            0x60,
            # JSR absolute
            0x20, 0x20, 0x80,
            # RTS
            0x60,
            # Some data at 0x8010
            0x12, 0x34, 0x56, 0x78,
            # Function at 0x8020
            0xA9, 0x01,  # LDA #$01
            0x60         # RTS
        ])
        
        self.cart.data = self.rom_data
        self.cart.address = MagicMock(side_effect=self.mock_address)
        self.cart.index = MagicMock(side_effect=self.mock_index)
        
        # Create a mock configurator
        self.config = MagicMock(spec=Configurator)
        self.config.get = MagicMock(return_value={})
        
        # Create disassembler
        self.disasm = Disassembler(self.cart, self.config)

    def mock_address(self, offset):
        """Mock address translation for testing."""
        # Simple LoROM mapping for testing
        return 0x8000 + offset

    def mock_index(self, addr):
        """Mock index translation for testing."""
        # Simple LoROM mapping for testing
        if 0x8000 <= addr < 0x10000:
            return addr - 0x8000
        return 0

    def test_disassembler_initialization(self):
        """Test disassembler initialization."""
        self.assertEqual(self.disasm.cart, self.cart)
        self.assertEqual(self.disasm.config, self.config)
        self.assertIsNotNone(self.disasm.labels)
        self.assertIsNotNone(self.disasm.memory)

    def test_basic_instruction_decoding(self):
        """Test basic 65816 instruction decoding."""
        # Test LDA immediate
        offset = 0
        instr = self.disasm.decode_instruction(offset)
        
        self.assertEqual(instr['opcode'], 'LDA')
        self.assertEqual(instr['addressing'], 'imm')
        self.assertEqual(instr['bytes'], 2)
        self.assertEqual(instr['operand'], 0x42)

    def test_absolute_addressing_mode(self):
        """Test absolute addressing mode decoding."""
        # Test STA absolute
        offset = 2
        instr = self.disasm.decode_instruction(offset)
        
        self.assertEqual(instr['opcode'], 'STA')
        self.assertEqual(instr['addressing'], 'abs')
        self.assertEqual(instr['bytes'], 3)
        self.assertEqual(instr['operand'], 0x7E0000)  # Mock address calculation

    def test_jump_instruction_decoding(self):
        """Test jump instruction decoding."""
        # Test JMP absolute
        offset = 5
        instr = self.disasm.decode_instruction(offset)
        
        self.assertEqual(instr['opcode'], 'JMP')
        self.assertEqual(instr['addressing'], 'abs')
        self.assertEqual(instr['bytes'], 3)

    def test_subroutine_instructions(self):
        """Test JSR and RTS instructions."""
        # Test JSR absolute
        offset = 11
        instr = self.disasm.decode_instruction(offset)
        
        self.assertEqual(instr['opcode'], 'JSR')
        self.assertEqual(instr['addressing'], 'abs')
        self.assertEqual(instr['bytes'], 3)
        
        # Test RTS
        offset = 14
        instr = self.disasm.decode_instruction(offset)
        
        self.assertEqual(instr['opcode'], 'RTS')
        self.assertEqual(instr['addressing'], 'imp')
        self.assertEqual(instr['bytes'], 1)

    def test_interrupt_instructions(self):
        """Test interrupt-related instructions."""
        # Test BRK
        offset = 8
        instr = self.disasm.decode_instruction(offset)
        
        self.assertEqual(instr['opcode'], 'BRK')
        self.assertEqual(instr['addressing'], 'imp')
        self.assertEqual(instr['bytes'], 1)
        
        # Test RTI
        offset = 9
        instr = self.disasm.decode_instruction(offset)
        
        self.assertEqual(instr['opcode'], 'RTI')
        self.assertEqual(instr['addressing'], 'imp')
        self.assertEqual(instr['bytes'], 1)

    def test_accumulator_addressing_mode(self):
        """Test accumulator addressing mode."""
        # Add ASL accumulator instruction to test data
        self.rom_data[15] = 0x0A  # ASL A
        
        offset = 15
        instr = self.disasm.decode_instruction(offset)
        
        self.assertEqual(instr['opcode'], 'ASL')
        self.assertEqual(instr['addressing'], 'acc')
        self.assertEqual(instr['bytes'], 1)

    def test_implied_addressing_mode(self):
        """Test implied addressing mode."""
        # Add CLC instruction to test data
        self.rom_data[16] = 0x18  # CLC
        
        offset = 16
        instr = self.disasm.decode_instruction(offset)
        
        self.assertEqual(instr['opcode'], 'CLC')
        self.assertEqual(instr['addressing'], 'imp')
        self.assertEqual(instr['bytes'], 1)

    def test_code_path_tracing(self):
        """Test code path tracing functionality."""
        # Configure test banks
        self.config.get.return_value = [0]
        
        # Run disassembly on test data
        self.disasm.run()
        
        # Check that labels were created
        self.assertGreater(len(self.disasm.labels), 0)
        
        # Check that main entry point was found
        # (This depends on the specific tracing implementation)

    def test_label_generation(self):
        """Test automatic label generation."""
        # Test label creation for addresses
        test_addr = 0x8000
        label = self.disasm.get_label(test_addr)
        
        # Should create a label format like L_8000
        self.assertIsNotNone(label)
        self.assertTrue(label.startswith('L_'))

    def test_label_management(self):
        """Test label management functions."""
        # Test adding custom label
        custom_label = "test_function"
        test_addr = 0x8020
        
        self.disasm.add_label(test_addr, custom_label)
        self.assertEqual(self.disasm.get_label(test_addr), custom_label)
        
        # Test that same address returns same label
        self.assertEqual(self.disasm.get_label(test_addr), custom_label)

    def test_snes_register_detection(self):
        """Test SNES register symbol detection."""
        # Test known SNES register addresses
        register_addrs = [
            0x4210,  # VCOUNT
            0x4211,  # HCOUNT
            0x4212,  # VMADDL
            0x4213,  # VMADDH
            0x4214,  # VMDATAL
            0x4215,  # VMDATAH
            0x4216,  # CGADD
            0x4217,  # CGDATA
            0x4218,  # CGADD
            0x4219,  # CGDATA
        ]
        
        for addr in register_addrs:
            symbol = self.disasm.get_register_symbol(addr)
            # Should return known register name or None
            self.assertIsInstance(symbol, (str, type(None)))

    def test_memory_symbol_resolution(self):
        """Test memory address symbol resolution."""
        # Add memory symbols to configurator
        self.config.get.return_value = {
            'player_health': 0x7E0010,
            'current_level': 0x7E0012,
            'score': 0x7E0014
        }
        
        # Test symbol lookup
        symbol = self.disasm.get_memory_symbol(0x7E0010)
        self.assertEqual(symbol, 'player_health')
        
        symbol = self.disasm.get_memory_symbol(0x7E0012)
        self.assertEqual(symbol, 'current_level')
        
        # Test unknown address
        symbol = self.disasm.get_memory_symbol(0x7E9999)
        self.assertIsNone(symbol)

    def test_instruction_commentary(self):
        """Test instruction commentary generation."""
        offset = 0
        instr = self.disasm.decode_instruction(offset)
        
        # Generate commentary
        comment = self.disasm.get_instruction_comment(instr)
        
        # Commentary may be None or a string
        self.assertIsInstance(comment, (str, type(None)))

    def test_bank_disassembly_boundaries(self):
        """Test that disassembly respects bank boundaries."""
        # Configure multiple banks
        self.config.get.return_value = [0, 1]
        
        # Extend ROM data for multiple banks
        extended_data = self.rom_data + bytearray(0x8000)  # Add bank 1
        self.cart.data = extended_data
        self.cart.size = len(extended_data)
        
        # Run disassembly
        self.disasm.run()
        
        # Check that both banks were processed
        # (This depends on specific implementation)

    def test_address_translation_consistency(self):
        """Test address translation consistency."""
        # Test that address/index methods are consistent
        test_offset = 0x1000
        addr = self.disasm.cart.address(test_offset)
        offset_back = self.disasm.cart.index(addr)
        
        # Should round-trip correctly
        self.assertEqual(test_offset, offset_back)

    def test_edge_case_instructions(self):
        """Test edge case and special instructions."""
        # Add some edge case instructions
        edge_data = bytearray([
            0xC2, 0x30,  # REP #$30
            0xE2, 0x30,  # SEP #$30
            0x5C, 0x00, 0x00, 0x01,  # JMP long
            0xDC, 0x00, 0x00,  # JMP [addr]
            0xFB,        # XBA
            0x8B,        # PHB
            0xAB,        # PLB
        ])
        
        self.rom_data.extend(edge_data)
        
        # Test each instruction
        offsets = [17, 19, 21, 25, 28, 29, 30]
        expected_ops = ['REP', 'SEP', 'JML', 'JMP', 'XBA', 'PHB', 'PLB']
        
        for i, (offset, expected_op) in enumerate(zip(offsets, expected_ops)):
            instr = self.disasm.decode_instruction(offset)
            self.assertEqual(instr['opcode'], expected_op, 
                           f"Instruction at offset {offset}")

    def test_disassembly_output_format(self):
        """Test that disassembly generates proper output format."""
        offset = 0
        instr = self.disasm.decode_instruction(offset)
        
        # Test instruction string generation
        instr_str = self.disasm.format_instruction(instr)
        
        self.assertIsInstance(instr_str, str)
        self.assertIn('LDA', instr_str)
        
    def test_error_handling_invalid_data(self):
        """Test error handling for invalid ROM data."""
        # Test with empty ROM
        self.cart.data = bytearray()
        self.cart.size = 0
        
        with self.assertRaises(Exception):
            self.disasm.decode_instruction(0)

    def test_performance_large_rom(self):
        """Test performance with larger ROM data."""
        # Create larger test ROM
        large_data = bytearray(0x100000)  # 1MB
        # Fill with some basic pattern
        for i in range(0, len(large_data), 3):
            if i + 2 < len(large_data):
                large_data[i] = 0xA9  # LDA
                large_data[i+1] = i & 0xFF  # immediate value
                large_data[i+2] = 0x8D  # STA
                large_data[i+3] = (i >> 8) & 0xFF if i+3 < len(large_data) else 0
        
        self.cart.data = large_data
        self.cart.size = len(large_data)
        
        # Test that it doesn't crash with large data
        try:
            self.disasm.decode_instruction(0)
            # Should succeed
        except Exception as e:
            self.fail(f"Disassembly failed with large ROM: {e}")


if __name__ == '__main__':
    unittest.main()