# -*- coding: utf-8 -*-

import unittest

from snes2asm.compression import hal

class HalTest(unittest.TestCase):

	def test_empty_data(self):
		"""Test compression of empty data."""
		empty = bytearray([])
		self.assertEqual(empty, hal.decompress(hal.compress(empty)))

	def test_single_byte(self):
		"""Test compression of a single byte."""
		singleByte = bytearray([65])
		self.assertEqual(singleByte, hal.decompress(hal.compress(singleByte)))

	def test_literal_data(self):
		"""Test compression of literal (uncompressible) data."""
		# Sequential unique bytes don't compress well
		literal = bytearray(range(256))
		self.assertEqual(literal, hal.decompress(hal.compress(literal)))

	def test_8bit_rle(self):
		"""Test 8-bit RLE compression."""
		# Repeated single byte
		rle8_short = bytearray([0x42] * 10)
		self.assertEqual(rle8_short, hal.decompress(hal.compress(rle8_short)))

		# Long RLE
		rle8_long = bytearray([0xAA] * 500)
		self.assertEqual(rle8_long, hal.decompress(hal.compress(rle8_long)))

	def test_16bit_rle(self):
		"""Test 16-bit RLE compression."""
		# Repeated 16-bit pattern
		rle16 = bytearray([0x12, 0x34] * 100)
		compressed = hal.compress(rle16)
		decompressed = hal.decompress(compressed)
		self.assertEqual(rle16, decompressed)

		# Check that it actually compresses well
		self.assertLess(len(compressed), len(rle16) / 10)

	def test_sequence_rle(self):
		"""Test sequence RLE compression (incrementing bytes)."""
		# Incrementing sequence
		sequence = bytearray(range(50))
		# Use non-fast mode to enable sequence RLE
		compressed = hal.compress(sequence, fast=False)
		decompressed = hal.decompress(compressed)
		self.assertEqual(sequence, decompressed)

	def test_pattern_backref(self):
		"""Test back reference compression with repeated patterns."""
		pattern = b"PATTERN123"
		repeated = bytearray(pattern * 50)
		compressed = hal.compress(repeated)
		decompressed = hal.decompress(compressed)
		self.assertEqual(repeated, decompressed)

		# Should compress significantly
		self.assertLess(len(compressed), len(repeated) / 5)

	def test_mixed_data(self):
		"""Test mixed compression with various patterns."""
		mixed = bytearray(b'Hello' * 20 + b'\xFF' * 100 + bytes(range(50)) + b'World' * 30)
		self.assertEqual(mixed, hal.decompress(hal.compress(mixed)))

	def test_string_compression(self):
		"""Test compression of string data."""
		stringBytes = bytearray("aaaaaaaaaaccaa".encode('utf-8'))
		self.assertEqual(stringBytes, hal.decompress(hal.compress(stringBytes)))

		stringBytes = bytearray("The quick brown fox jumps over the lazy dog. " * 10, 'utf-8')
		self.assertEqual(stringBytes, hal.decompress(hal.compress(stringBytes)))

	def test_fast_mode(self):
		"""Test fast compression mode."""
		data = bytearray(b'Test data for fast compression. ' * 20)

		# Both modes should produce valid output
		fast_compressed = hal.compress(data, fast=True)
		normal_compressed = hal.compress(data, fast=False)

		self.assertEqual(data, hal.decompress(fast_compressed))
		self.assertEqual(data, hal.decompress(normal_compressed))

		# Fast mode might produce larger output, but both should work
		self.assertGreater(len(fast_compressed), 0)
		self.assertGreater(len(normal_compressed), 0)

	def test_large_data(self):
		"""Test compression of larger data blocks."""
		# Test with 4KB of data
		large = bytearray([i % 256 for i in range(4096)])
		self.assertEqual(large, hal.decompress(hal.compress(large)))

	def test_all_zeros(self):
		"""Test compression of all zeros (best case for RLE)."""
		zeros = bytearray([0] * 1000)
		compressed = hal.compress(zeros)
		self.assertEqual(zeros, hal.decompress(compressed))

		# Should compress extremely well (1000 bytes -> ~4 bytes)
		self.assertLess(len(compressed), 10)

	def test_all_ones(self):
		"""Test compression of all 0xFF bytes."""
		ones = bytearray([0xFF] * 1000)
		compressed = hal.compress(ones)
		self.assertEqual(ones, hal.decompress(compressed))

		# Should compress extremely well
		self.assertLess(len(compressed), 10)

	def test_alternating_pattern(self):
		"""Test compression of alternating byte patterns."""
		# 0xAA 0x55 pattern (common in graphics)
		pattern = bytearray([0xAA, 0x55] * 200)
		compressed = hal.compress(pattern)
		decompressed = hal.decompress(compressed)
		self.assertEqual(pattern, decompressed)

		# Should use 16-bit RLE
		self.assertLess(len(compressed), 20)

	def test_tile_data_pattern(self):
		"""Test with pattern similar to SNES tile data."""
		# Simulate 4bpp tile data (2 bitplanes, repeated patterns)
		tile_pattern = bytearray([0x00, 0x00, 0xFF, 0xFF, 0xAA, 0x55, 0x33, 0xCC])
		tile_data = bytearray(tile_pattern * 32)  # 32 tiles worth

		compressed = hal.compress(tile_data)
		decompressed = hal.decompress(compressed)
		self.assertEqual(tile_data, decompressed)

	def test_specific_compressed_output(self):
		"""Test that specific input produces expected compressed format."""
		# Test 8-bit RLE: 10 bytes of 0x42
		data = bytearray([0x42] * 10)
		compressed = hal.compress(data)

		# Should be: [command_byte, value, terminator]
		# Command for RLE-8 with length 10-1=9: 0x20 + (0 << 5) | 9 = 0x29
		expected = bytearray([0x29, 0x42, 0xFF])
		self.assertEqual(expected, compressed)

	def test_specific_16bit_rle_output(self):
		"""Test 16-bit RLE produces correct format."""
		# Test 16-bit RLE: 10 repetitions of 0x1234
		data = bytearray([0x12, 0x34] * 10)
		compressed = hal.compress(data)

		# Command for RLE-16 with length (10-1)=9: 0x20 + (1 << 5) | 9 = 0x49
		# 16-bit value is stored as little-endian: 0x12, 0x34
		expected = bytearray([0x49, 0x12, 0x34, 0xFF])
		self.assertEqual(expected, compressed)

	def test_decompress_known_data(self):
		"""Test decompression of known compressed data."""
		# Compressed: 8-bit RLE of 5 bytes of 0x99
		# Command: 0x20 + (0 << 5) | 4 = 0x24 (length 5)
		compressed = bytearray([0x24, 0x99, 0xFF])
		expected = bytearray([0x99] * 5)
		self.assertEqual(expected, hal.decompress(compressed))

	def test_decompress_16bit_known_data(self):
		"""Test decompression of known 16-bit RLE data."""
		# Compressed: 16-bit RLE of 3 repetitions of 0xABCD
		# Command: 0x20 + (1 << 5) | 2 = 0x42 (length 3)
		compressed = bytearray([0x42, 0xCD, 0xAB, 0xFF])
		expected = bytearray([0xCD, 0xAB, 0xCD, 0xAB, 0xCD, 0xAB])
		self.assertEqual(expected, hal.decompress(compressed))

	def test_decompress_literal_data(self):
		"""Test decompression of literal (uncompressed) data."""
		# Command 0x00: literal data, 3 bytes
		# Command: 0x00 | 2 = 0x02 (length 3)
		compressed = bytearray([0x02, 0x41, 0x42, 0x43, 0xFF])
		expected = bytearray([0x41, 0x42, 0x43])
		self.assertEqual(expected, hal.decompress(compressed))

	def test_long_run_compression(self):
		"""Test compression of runs longer than 32 bytes."""
		# Test long run (> RUN_SIZE of 32)
		long_run = bytearray([0x77] * 200)
		compressed = hal.compress(long_run)
		decompressed = hal.decompress(compressed)
		self.assertEqual(long_run, decompressed)

	def test_bytes_input(self):
		"""Test that bytes (not just bytearray) work as input."""
		data = b"Test with bytes type"
		compressed = hal.compress(data)
		decompressed = hal.decompress(compressed)
		self.assertEqual(bytearray(data), decompressed)

	def test_roundtrip_consistency(self):
		"""Test that multiple compress/decompress cycles are consistent."""
		data = bytearray(b"Consistency test data! " * 20)

		# First cycle
		compressed1 = hal.compress(data)
		decompressed1 = hal.decompress(compressed1)

		# Second cycle
		compressed2 = hal.compress(decompressed1)
		decompressed2 = hal.decompress(compressed2)

		# All should be equal
		self.assertEqual(data, decompressed1)
		self.assertEqual(data, decompressed2)
		self.assertEqual(compressed1, compressed2)


if __name__ == '__main__':
	unittest.main()
