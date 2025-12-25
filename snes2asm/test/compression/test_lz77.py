"""
Unit tests for LZ77 compression/decompression
"""

import unittest
from snes2asm.compression import lz77


class TestLZ77(unittest.TestCase):
    """Test cases for LZ77 compression and decompression"""

    def test_empty_data(self):
        """Test compression and decompression of empty data"""
        data = b''
        compressed = lz77.compress(data)
        decompressed = lz77.decompress(compressed)
        self.assertEqual(decompressed, data)

    def test_single_byte(self):
        """Test compression of a single byte"""
        data = b'\x42'
        compressed = lz77.compress(data)
        decompressed = lz77.decompress(compressed)
        self.assertEqual(decompressed, data)

    def test_all_literals(self):
        """Test data with no repeated patterns (all literals)"""
        data = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09'
        compressed = lz77.compress(data)
        decompressed = lz77.decompress(compressed)
        self.assertEqual(decompressed, data)

    def test_simple_repetition(self):
        """Test simple repeated pattern"""
        data = b'AAABBBCCC'
        compressed = lz77.compress(data)
        decompressed = lz77.decompress(compressed)
        self.assertEqual(decompressed, data)

    def test_long_repetition(self):
        """Test long repeated sequence"""
        data = b'ABCDEFGH' * 10
        compressed = lz77.compress(data)
        decompressed = lz77.decompress(compressed)
        self.assertEqual(decompressed, data)
        # Compression should reduce size
        self.assertLess(len(compressed), len(data))

    def test_run_length_encoding(self):
        """Test run-length encoding (overlapping copy)"""
        # Pattern like 'AAAAAAA...' where offset=1, length>1
        data = b'A' * 100
        compressed = lz77.compress(data)
        decompressed = lz77.decompress(compressed)
        self.assertEqual(decompressed, data)
        # Should compress very well
        self.assertLess(len(compressed), len(data) // 2)

    def test_mixed_patterns(self):
        """Test data with mixed literals and references"""
        data = b'Hello World! Hello World! Goodbye World!'
        compressed = lz77.compress(data)
        decompressed = lz77.decompress(compressed)
        self.assertEqual(decompressed, data)

    def test_binary_data(self):
        """Test compression of binary data"""
        data = bytes(range(256)) + bytes(range(256))
        compressed = lz77.compress(data)
        decompressed = lz77.decompress(compressed)
        self.assertEqual(decompressed, data)

    def test_minimum_match_length(self):
        """Test that matches shorter than 3 bytes are not encoded"""
        # Pattern with 2-byte repeats (should use literals)
        data = b'ABABABABAB'
        compressed = lz77.compress(data)
        decompressed = lz77.decompress(compressed)
        self.assertEqual(decompressed, data)

    def test_maximum_match_length(self):
        """Test maximum match length (18 bytes)"""
        # Create pattern longer than max match
        pattern = b'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        data = pattern + pattern + pattern
        compressed = lz77.compress(data)
        decompressed = lz77.decompress(compressed)
        self.assertEqual(decompressed, data)

    def test_sliding_window_limit(self):
        """Test that matches beyond window size (4096) are not found"""
        # Create data where potential match is beyond window
        filler = b'\x00' * 5000  # Push potential match out of window
        pattern = b'PATTERN'
        data = pattern + filler + pattern
        compressed = lz77.compress(data)
        decompressed = lz77.decompress(compressed)
        self.assertEqual(decompressed, data)

    def test_bytearray_input(self):
        """Test that bytearray input works"""
        data = bytearray(b'Test data with bytearray')
        compressed = lz77.compress(data)
        decompressed = lz77.decompress(compressed)
        self.assertEqual(decompressed, bytes(data))

    def test_snes_graphics_like_data(self):
        """Test with SNES graphics-like data (repeating tile patterns)"""
        # Simulate 4bpp tile data with repetition
        tile = b'\x00\xFF\x0F\xF0\x33\xCC\x55\xAA' * 4  # 32-byte tile
        data = tile * 20  # 20 tiles
        compressed = lz77.compress(data)
        decompressed = lz77.decompress(compressed)
        self.assertEqual(decompressed, data)
        # Should compress well
        self.assertLess(len(compressed), len(data) // 3)

    def test_snes_tilemap_like_data(self):
        """Test with SNES tilemap-like data"""
        # Tilemaps often have repeated tile indices
        data = b'\x00\x00\x01\x01\x02\x02' * 50
        compressed = lz77.compress(data)
        decompressed = lz77.decompress(compressed)
        self.assertEqual(decompressed, data)

    def test_worst_case_random_data(self):
        """Test with random-like data (worst case for compression)"""
        # Pseudo-random sequence unlikely to compress well
        data = bytes([(i * 37 + 17) % 256 for i in range(1000)])
        compressed = lz77.compress(data)
        decompressed = lz77.decompress(compressed)
        self.assertEqual(decompressed, data)

    def test_incrementing_pattern(self):
        """Test with incrementing bytes"""
        data = bytes(range(256))
        compressed = lz77.compress(data)
        decompressed = lz77.decompress(compressed)
        self.assertEqual(decompressed, data)

    def test_alternating_pattern(self):
        """Test alternating byte pattern"""
        data = b'\xAA\x55' * 100
        compressed = lz77.compress(data)
        decompressed = lz77.decompress(compressed)
        self.assertEqual(decompressed, data)

    def test_compression_ratio_improvement(self):
        """Verify compression actually reduces size for redundant data"""
        # Highly redundant data should compress well
        data = b'The quick brown fox jumps over the lazy dog. ' * 50
        compressed = lz77.compress(data)
        decompressed = lz77.decompress(compressed)
        self.assertEqual(decompressed, data)
        # Should achieve at least 2:1 compression ratio
        self.assertLess(len(compressed), len(data) // 2)

    def test_decompress_empty(self):
        """Test decompressing empty data"""
        result = lz77.decompress(b'')
        self.assertEqual(result, b'')

    def test_invalid_input_type_compress(self):
        """Test that invalid input type raises TypeError"""
        with self.assertRaises(TypeError):
            lz77.compress("not bytes")

    def test_invalid_input_type_decompress(self):
        """Test that invalid input type raises TypeError"""
        with self.assertRaises(TypeError):
            lz77.decompress("not bytes")


class TestLZ77EdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""

    def test_exact_match_at_window_boundary(self):
        """Test match exactly at window size boundary"""
        # Create a pattern, then fill exactly 4096 bytes, then repeat
        pattern = b'BOUNDARY'
        filler = b'\x00' * (4096 - len(pattern))
        data = pattern + filler + pattern
        compressed = lz77.compress(data)
        decompressed = lz77.decompress(compressed)
        self.assertEqual(decompressed, data)

    def test_overlapping_copy_edge_case(self):
        """Test overlapping copy with offset=1"""
        # This tests the case where we copy from position (current-1)
        # which creates a run-length pattern
        data = b'X' + b'Y' * 50
        compressed = lz77.compress(data)
        decompressed = lz77.decompress(compressed)
        self.assertEqual(decompressed, data)

    def test_match_at_end_of_data(self):
        """Test that match at very end of data works correctly"""
        data = b'START' + b'X' * 100 + b'END' + b'END'
        compressed = lz77.compress(data)
        decompressed = lz77.decompress(compressed)
        self.assertEqual(decompressed, data)

    def test_all_same_byte(self):
        """Test data that is entirely the same byte"""
        data = b'\x7F' * 500
        compressed = lz77.compress(data)
        decompressed = lz77.decompress(compressed)
        self.assertEqual(decompressed, data)
        # Should compress extremely well (less than 15% of original)
        self.assertLess(len(compressed), 75)


if __name__ == '__main__':
    unittest.main()
