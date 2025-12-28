# -*- coding: utf-8 -*-

import unittest
from snes2asm.decoder import StructDecoder, ArrayDecoder, Decoder, IndexDecoder


class StructDecoderTest(unittest.TestCase):
	"""Test cases for StructDecoder and ArrayDecoder with struct support."""

	def test_simple_struct_fields(self):
		"""Test StructDecoder with simple integer fields."""
		# Test data: 3 structs with fields hp(1), strength(1), wisdom(1)
		test_data = bytes([
			0x64, 0x12, 0x08,  # Struct 0: hp=100, strength=18, wisdom=8
			0x32, 0x0A, 0x0F,  # Struct 1: hp=50, strength=10, wisdom=15
			0x78, 0x14, 0x0C,  # Struct 2: hp=120, strength=20, wisdom=12
		])

		fields = {
			'hp': 1,
			'strength': 1,
			'wisdom': 1
		}

		decoder = StructDecoder(
			label='enemy_stats',
			start=0x1F000,
			end=0x1F009,
			fields=fields
		)

		# Verify struct size calculation
		self.assertEqual(decoder.struct_size, 3)
		self.assertEqual(decoder.count, 3)

		# Verify generated instructions
		instructions = list(decoder.decode(test_data))

		# First struct should have label
		self.assertEqual(instructions[0][0], 0)
		self.assertIn('enemy_stats_0:', instructions[0][1].text())
		self.assertIn('$64', instructions[0][1].text())
		self.assertIn('hp', instructions[0][1].text())

		# Verify all 9 fields are generated (3 structs * 3 fields)
		self.assertEqual(len(instructions), 9)

	def test_single_struct(self):
		"""Test StructDecoder with count=1 (single struct)."""
		test_data = bytes([0x20, 0x10, 0x42, 0x03])

		fields = {
			'width': 1,
			'height': 1,
			'tileset_id': 2
		}

		decoder = StructDecoder(
			label='level_header',
			start=0x10000,
			end=0x10004,
			fields=fields
		)

		# Verify single struct
		self.assertEqual(decoder.count, 1)
		self.assertEqual(decoder.struct_size, 4)

		instructions = list(decoder.decode(test_data))

		# Should have label without _0 suffix for single struct
		self.assertIn('level_header:', instructions[0][1].text())
		self.assertNotIn('level_header_0:', instructions[0][1].text())

	def test_explicit_count(self):
		"""Test StructDecoder with explicit count parameter."""
		test_data = bytes([
			0x01, 0x02,
			0x03, 0x04,
		])

		fields = {'value': 2}

		decoder = StructDecoder(
			label='test_data',
			start=0x0000,
			end=0x0004,
			count=2,
			fields=fields
		)

		self.assertEqual(decoder.count, 2)
		self.assertEqual(decoder.struct_size, 2)

	def test_bitfield_struct(self):
		"""Test StructDecoder with bitfield fields."""
		# Test data: tilemap entry with bit-packed fields
		# 16-bit value: 0x7C42 = tile_id=0x042, x_flip=1, y_flip=1, palette=7, priority=0
		test_data = bytes([0x42, 0x7C])

		fields = {
			'tile_entry': {
				'size': 2,
				'bitfields': {
					'tile_id': {'bits': '0-9', 'mask': 0x03FF},
					'x_flip': {'bit': 10},
					'y_flip': {'bit': 11},
					'palette': {'bits': '12-14', 'mask': 0x7000, 'shift': 12},
					'priority': {'bit': 15}
				}
			}
		}

		decoder = StructDecoder(
			label='tilemap',
			start=0x8000,
			end=0x8002,
			fields=fields
		)

		self.assertEqual(decoder.struct_size, 2)
		self.assertEqual(decoder.count, 1)

		instructions = list(decoder.decode(test_data))

		# Verify bitfield expression is generated
		instruction_text = instructions[0][1].text()
		self.assertIn('.dw', instruction_text)
		self.assertIn('<<', instruction_text)  # Shift operators
		self.assertIn('|', instruction_text)   # OR operators
		self.assertIn('tile_entry:', instruction_text)  # Field name in comment
		self.assertIn('tile_id=', instruction_text)     # Bitfield values in comment

	def test_mixed_fields(self):
		"""Test StructDecoder with both simple and bitfield fields."""
		test_data = bytes([
			0x20, 0x10,        # width=32, height=16
			0x42, 0x7C,        # tilemap entry (bitfields)
			0x03,              # music_id=3
		])

		fields = {
			'width': 1,
			'height': 1,
			'tilemap_flags': {
				'size': 2,
				'bitfields': {
					'tile_id': {'bits': '0-9', 'mask': 0x03FF},
					'x_flip': {'bit': 10},
					'y_flip': {'bit': 11},
					'palette': {'bits': '12-14', 'mask': 0x7000, 'shift': 12},
				}
			},
			'music_id': 1
		}

		decoder = StructDecoder(
			label='level_header',
			start=0x10000,
			end=0x10005,
			fields=fields
		)

		self.assertEqual(decoder.struct_size, 5)
		self.assertEqual(decoder.count, 1)

		instructions = list(decoder.decode(test_data))

		# Should have 4 instructions (4 fields)
		self.assertEqual(len(instructions), 4)

		# First field should be simple
		self.assertIn('.db $20', instructions[0][1].text())
		self.assertIn('width', instructions[0][1].text())

		# Third field should have bitfield expression
		self.assertIn('tilemap_flags:', instructions[2][1].text())
		self.assertIn('<<', instructions[2][1].text())

	def test_array_with_struct(self):
		"""Test ArrayDecoder with struct parameter."""
		test_data = bytes([
			0x64, 0x12, 0x08, 0x42, 0x7C,  # Enemy 0
			0x32, 0x0A, 0x0F, 0x05, 0x31,  # Enemy 1
		])

		struct_def = {
			'hp': 1,
			'strength': 1,
			'wisdom': 1,
			'sprite_data': {
				'size': 2,
				'bitfields': {
					'tile_id': {'bits': '0-9', 'mask': 0x03FF},
					'x_flip': {'bit': 10},
					'y_flip': {'bit': 11},
					'palette': {'bits': '12-14', 'mask': 0x7000, 'shift': 12},
				}
			}
		}

		decoder = ArrayDecoder(
			label='enemy_array',
			start=0x2F000,
			end=0x2F00A,
			struct=struct_def
		)

		self.assertEqual(decoder.size, 5)  # Total struct size

		instructions = list(decoder.decode(test_data))

		# Should have 8 instructions (2 enemies * 4 fields)
		self.assertEqual(len(instructions), 8)

		# First instruction should have array label
		self.assertIn('enemy_array_0:', instructions[0][1].text())

	def test_array_simple_struct(self):
		"""Test ArrayDecoder with simple struct (no bitfields)."""
		test_data = bytes([
			0x01, 0x00, 0x64, 0x00, 0x01, 0x05,  # Item 0
			0x02, 0x00, 0xC8, 0x00, 0x02, 0x03,  # Item 1
		])

		struct_def = {
			'item_id': 2,
			'cost': 2,
			'effect_type': 1,
			'effect_power': 1
		}

		decoder = ArrayDecoder(
			label='item_stats',
			start=0x30000,
			end=0x3000C,
			struct=struct_def
		)

		self.assertEqual(decoder.size, 6)

		instructions = list(decoder.decode(test_data))

		# Should have 8 instructions (2 items * 4 fields)
		self.assertEqual(len(instructions), 8)

	def test_struct_size_validation(self):
		"""Test that struct size validation works correctly."""
		fields = {
			'hp': 1,
			'strength': 1,
			'wisdom': 1
		}

		# This should raise an error: data size (10) doesn't align with struct size (3)
		with self.assertRaises(ValueError) as context:
			decoder = StructDecoder(
				label='test',
				start=0x0000,
				end=0x000A,  # 10 bytes, not divisible by 3
				fields=fields
			)

		self.assertIn('does not align with struct size', str(context.exception))

	def test_struct_explicit_count_mismatch(self):
		"""Test that explicit count validation works."""
		fields = {'value': 2}

		# This should raise an error: count=5 * size=2 = 10, but data is only 8 bytes
		with self.assertRaises(ValueError) as context:
			decoder = StructDecoder(
				label='test',
				start=0x0000,
				end=0x0008,
				count=5,  # 5 * 2 = 10 bytes expected
				fields=fields
			)

		self.assertIn('size mismatch', str(context.exception))

	def test_missing_fields_parameter(self):
		"""Test that missing fields parameter raises error."""
		with self.assertRaises(ValueError) as context:
			decoder = StructDecoder(
				label='test',
				start=0x0000,
				end=0x0004
				# Missing fields parameter
			)

		self.assertIn('missing', str(context.exception))

	def test_bitfield_single_bit(self):
		"""Test bitfield with single bit definition."""
		test_data = bytes([0x01, 0x04])  # bit 10 set

		fields = {
			'flags': {
				'size': 2,
				'bitfields': {
					'enabled': {'bit': 0},
					'x_flip': {'bit': 10}
				}
			}
		}

		decoder = StructDecoder(
			label='test_flags',
			start=0x0000,
			end=0x0002,
			fields=fields
		)

		instructions = list(decoder.decode(test_data))

		# Verify shift operators for single bits
		instruction_text = instructions[0][1].text()
		self.assertIn('<<', instruction_text)

	def test_bitfield_range(self):
		"""Test bitfield with bit range definition."""
		test_data = bytes([0xFF, 0x03])  # Lower 10 bits all set

		fields = {
			'value': {
				'size': 2,
				'bitfields': {
					'tile_id': {'bits': '0-9', 'mask': 0x03FF}
				}
			}
		}

		decoder = StructDecoder(
			label='test_range',
			start=0x0000,
			end=0x0002,
			fields=fields
		)

		instructions = list(decoder.decode(test_data))

		instruction_text = instructions[0][1].text()
		# Should extract value 0x3FF from the data
		self.assertIn('03FF', instruction_text)

	def test_field_offset_calculation(self):
		"""Test that field offsets are calculated correctly."""
		test_data = bytes([
			0x01, 0x02, 0x03, 0x04, 0x05,  # 1 + 2 + 1 + 1 bytes
		])

		fields = {
			'field1': 1,
			'field2': 2,
			'field3': 1,
			'field4': 1
		}

		decoder = StructDecoder(
			label='test_offsets',
			start=0x0000,
			end=0x0005,
			fields=fields
		)

		instructions = list(decoder.decode(test_data))

		# Verify offsets
		self.assertEqual(instructions[0][0], 0)  # field1 at offset 0
		self.assertEqual(instructions[1][0], 1)  # field2 at offset 1
		self.assertEqual(instructions[2][0], 3)  # field3 at offset 3
		self.assertEqual(instructions[3][0], 4)  # field4 at offset 4


	def test_array_with_index(self):
		"""Test ArrayDecoder with IndexDecoder."""
		# Test data: index table + struct data
		test_data = bytes([
			# Index table (3 entries * 2 bytes)
			0x00, 0x00,  # Offset 0
			0x04, 0x00,  # Offset 4
			0x08, 0x00,  # Offset 8
			# Struct data
			0x00, 0x01, 0x00, 0x02,  # Struct 0
			0x00, 0x03, 0x00, 0x04,  # Struct 1
			0x00, 0x05, 0x00, 0x06,  # Struct 2
		])

		# Create index decoder
		index_decoder = IndexDecoder(
			label='struct_index',
			start=0x1000,
			end=0x1006,
			size=2
		)

		# Create array with index
		array_decoder = ArrayDecoder(
			label='indexed_structs',
			start=0x1006,
			end=0x1012,
			struct={
				'id': 2,
				'value': 2
			},
			index=index_decoder
		)

		# Decode index first
		index_data = test_data[0:6]
		index_instructions = list(index_decoder.decode(index_data))

		# Verify index values
		self.assertEqual(index_decoder.values, [0, 4, 8])

		# Verify first index entry has both main and indexed labels
		first_index_text = index_instructions[0][1].text()
		self.assertIn('struct_index:', first_index_text)
		self.assertIn('struct_index_0:', first_index_text)

		# Decode array
		array_data = test_data[6:18]
		instructions = list(array_decoder.decode(array_data))

		# Should have 6 instructions (3 structs * 2 fields)
		self.assertEqual(len(instructions), 6)

		# Verify offsets are correct
		self.assertEqual(instructions[0][0], 0)  # Struct 0, field 0
		self.assertEqual(instructions[1][0], 2)  # Struct 0, field 1
		self.assertEqual(instructions[2][0], 4)  # Struct 1, field 0
		self.assertEqual(instructions[3][0], 6)  # Struct 1, field 1
		self.assertEqual(instructions[4][0], 8)  # Struct 2, field 0
		self.assertEqual(instructions[5][0], 10) # Struct 2, field 1

	def test_index_automatic_label_lookup(self):
		"""Test IndexDecoder with automatic label lookup from disassembler."""
		# Test data with 16-bit addresses (little-endian)
		test_data = bytes([
			0x00, 0x80,  # $8000 -> main_loop (has label)
			0x00, 0x81,  # $8100 -> handle_input (has label)
			0x00, 0x82,  # $8200 -> update_sprites (has label)
			0xFF, 0x7F,  # $7FFF -> no label (should use hex)
			0x00, 0x90,  # $9000 -> no label (should use hex)
		])

		# Create mock disassembler with code_labels
		class MockDisasm:
			def __init__(self):
				self.code_labels = {
					0x8000: 'main_loop',
					0x8100: 'handle_input',
					0x8200: 'update_sprites',
					# 0x7FFF and 0x9000 have no labels
				}

		# Create IndexDecoder
		index = IndexDecoder(
			label='function_table',
			start=0x1000,
			end=0x100A,  # 5 entries * 2 bytes
			size=2
		)

		# Set disasm reference
		index.disasm = MockDisasm()

		# Decode
		instructions = list(index.decode(test_data))

		# Should have 5 instructions
		self.assertEqual(len(instructions), 5)

		# First entry should have both main label and indexed label
		first_entry_text = instructions[0][1].text()
		self.assertIn('function_table:', first_entry_text)
		self.assertIn('function_table_0:', first_entry_text)
		self.assertIn('main_loop', first_entry_text)
		self.assertNotIn('$8000', first_entry_text)

		# Subsequent entries should only have indexed labels
		second_entry_text = instructions[1][1].text()
		self.assertNotIn('function_table:\n', second_entry_text)
		self.assertIn('function_table_1:', second_entry_text)
		self.assertIn('handle_input', second_entry_text)
		self.assertNotIn('$8100', second_entry_text)

		self.assertIn('update_sprites', instructions[2][1].text())
		self.assertNotIn('$8200', instructions[2][1].text())

		# Last 2 entries should use hex values (no labels)
		self.assertIn('$7FFF', instructions[3][1].text())
		self.assertNotIn('main_loop', instructions[3][1].text())
		self.assertNotIn('handle_input', instructions[3][1].text())

		self.assertIn('$9000', instructions[4][1].text())
		self.assertNotIn('main_loop', instructions[4][1].text())

	def test_index_with_24bit_label_lookup(self):
		"""Test IndexDecoder with 24-bit addresses and label lookup."""
		# Test data with 24-bit addresses (little-endian)
		test_data = bytes([
			0x00, 0x00, 0x80,  # $800000 -> rom_start (has label)
			0x00, 0x10, 0x80,  # $801000 -> level_1_data (has label)
			0xFF, 0xFF, 0x7F,  # $7FFFFF -> no label
		])

		# Create mock disassembler
		class MockDisasm:
			def __init__(self):
				self.code_labels = {
					0x800000: 'rom_start',
					0x801000: 'level_1_data',
				}

		# Create IndexDecoder with size=3 for 24-bit
		index = IndexDecoder(
			label='level_ptrs',
			start=0x2000,
			end=0x2009,  # 3 entries * 3 bytes
			size=3
		)

		index.disasm = MockDisasm()

		# Decode
		instructions = list(index.decode(test_data))

		# Should have 3 instructions
		self.assertEqual(len(instructions), 3)

		# First entry should have both main label and indexed label
		first_entry_text = instructions[0][1].text()
		self.assertIn('level_ptrs:', first_entry_text)
		self.assertIn('level_ptrs_0:', first_entry_text)

		# Should use .dl directive for 24-bit
		self.assertIn('.dl', first_entry_text)

		# First 2 should use labels
		self.assertIn('rom_start', first_entry_text)
		self.assertIn('level_1_data', instructions[1][1].text())

		# Last should use hex
		self.assertIn('$7FFFFF', instructions[2][1].text())

	def test_index_without_disasm_reference(self):
		"""Test IndexDecoder works without disasm reference (backward compatibility)."""
		test_data = bytes([
			0x00, 0x80,
			0x00, 0x81,
		])

		index = IndexDecoder(
			label='test_table',
			start=0x1000,
			end=0x1004,
			size=2
		)

		# Don't set disasm reference (None)
		self.assertIsNone(index.disasm)

		# Should still decode, just using hex values
		instructions = list(index.decode(test_data))

		self.assertEqual(len(instructions), 2)

		# First entry should have both main label and indexed label
		first_entry_text = instructions[0][1].text()
		self.assertIn('test_table:', first_entry_text)
		self.assertIn('test_table_0:', first_entry_text)
		self.assertIn('$8000', first_entry_text)

		# Second entry should only have indexed label
		second_entry_text = instructions[1][1].text()
		self.assertNotIn('test_table:\n', second_entry_text)
		self.assertIn('test_table_1:', second_entry_text)
		self.assertIn('$8100', second_entry_text)


if __name__ == '__main__':
	unittest.main()
