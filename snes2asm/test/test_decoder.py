# -*- coding: utf-8 -*-

import unittest
import os
from unittest.mock import patch, MagicMock
from snes2asm.cartridge import Cartridge
from snes2asm.decoder import *
from snes2asm.configurator import Configurator


class DecoderTest(unittest.TestCase):
    """Test asset decoder system for various data types."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock cartridge
        self.cart = MagicMock(spec=Cartridge)
        self.cart.address = MagicMock(return_value=0x8000)
        self.cart.index = MagicMock(return_value=0x1000)
        
        # Create test data patterns
        self.palette_data = bytearray([
            0x1F, 0x00,  # Red
            0x00, 0x1F,  # Blue  
            0x1F, 0x1F,  # Magenta
            0x00, 0x00,  # Black
            0x1F, 0x0F,  # Orange
            0x0F, 0x1F,  # Cyan
            0x0F, 0x0F,  # Gray
            0x1F, 0x1F,  # White
        ])
        
        self.gfx_2bpp_data = bytearray([
            # Simple 8x8 tile at 2bpp (16 bytes)
            0x00, 0x00, 0x00, 0x00, 0x01, 0x01, 0x01, 0x01,
            0x00, 0x00, 0x00, 0x00, 0x02, 0x02, 0x02, 0x02,
        ])
        
        self.gfx_4bpp_data = bytearray([
            # Simple 8x8 tile at 4bpp (32 bytes)
            0x00, 0x00, 0x00, 0x00, 0x11, 0x11, 0x11, 0x11,
            0x00, 0x00, 0x00, 0x00, 0x22, 0x22, 0x22, 0x22,
            0x00, 0x00, 0x00, 0x00, 0x33, 0x33, 0x33, 0x33,
            0x00, 0x00, 0x00, 0x00, 0x44, 0x44, 0x44, 0x44,
        ])
        
        self.tilemap_data = bytearray([
            # 4x4 tilemap with 16-bit entries
            0x00, 0x00, 0x01, 0x00, 0x02, 0x00, 0x03, 0x00,  # Row 0
            0x10, 0x00, 0x11, 0x00, 0x12, 0x00, 0x13, 0x00,  # Row 1
            0x20, 0x00, 0x21, 0x00, 0x22, 0x00, 0x23, 0x00,  # Row 2
            0x30, 0x00, 0x31, 0x00, 0x32, 0x00, 0x33, 0x00,  # Row 3
        ])
        
        self.array_data = bytearray([
            # Array of 8-bit values
            0x10, 0x20, 0x30, 0x40, 0x50, 0x60, 0x70, 0x80,
        ])
        
        self.index_data = bytearray([
            # Pointer table (16-bit pointers)
            0x00, 0x80,  # Pointer to 0x8000
            0x20, 0x80,  # Pointer to 0x8020
            0x40, 0x80,  # Pointer to 0x8040
        ])
        
        self.text_data = bytearray([
            # Simple encoded text
            0x41, 0x42, 0x43, 0x00,  # "ABC" + terminator
        ])
        
        self.brr_data = bytearray([
            # Simple BRR audio sample header
            0x0E,  # Header: loop flag + range
            # Sample data would follow...
        ] + [0x00] * 15)

    def test_palette_decoder_basic(self):
        """Test basic palette decoder functionality."""
        config = {
            'type': 'palette',
            'label': 'test_palette',
            'start': 0x1000,
            'end': 0x1000 + len(self.palette_data)
        }
        
        decoder = PaletteDecoder(self.cart, config)
        decoder.start = 0x1000
        decoder.end = 0x1000 + len(self.palette_data)
        
        # Mock cartridge data
        self.cart.data = self.palette_data
        self.cart.address.side_effect = lambda x: 0x8000 + (x - 0x1000)
        
        # Test decoding
        result = decoder.decode()
        
        self.assertIsInstance(result, str)
        self.assertIn('test_palette:', result)
        self.assertIn('.dw', result)

    def test_graphics_decoder_2bpp(self):
        """Test 2bpp graphics decoder."""
        config = {
            'type': 'gfx',
            'label': 'test_gfx_2bpp',
            'start': 0x1000,
            'end': 0x1000 + len(self.gfx_2bpp_data),
            'bit_depth': 2
        }
        
        decoder = GraphicDecoder(self.cart, config)
        decoder.start = 0x1000
        decoder.end = 0x1000 + len(self.gfx_2bpp_data)
        
        # Mock cartridge data
        self.cart.data = self.gfx_2bpp_data
        
        # Test decoding
        result = decoder.decode()
        
        self.assertIsInstance(result, str)
        self.assertIn('test_gfx_2bpp:', result)

    def test_graphics_decoder_4bpp(self):
        """Test 4bpp graphics decoder."""
        config = {
            'type': 'gfx',
            'label': 'test_gfx_4bpp',
            'start': 0x1000,
            'end': 0x1000 + len(self.gfx_4bpp_data),
            'bit_depth': 4
        }
        
        decoder = GraphicDecoder(self.cart, config)
        decoder.start = 0x1000
        decoder.end = 0x1000 + len(self.gfx_4bpp_data)
        
        # Mock cartridge data
        self.cart.data = self.gfx_4bpp_data
        
        # Test decoding
        result = decoder.decode()
        
        self.assertIsInstance(result, str)
        self.assertIn('test_gfx_4bpp:', result)

    def test_graphics_decoder_8bpp(self):
        """Test 8bpp graphics decoder."""
        config = {
            'type': 'gfx',
            'label': 'test_gfx_8bpp',
            'start': 0x1000,
            'end': 0x1000 + 64,  # 64 bytes for 8bpp 8x8 tile
            'bit_depth': 8
        }
        
        decoder = GraphicDecoder(self.cart, config)
        decoder.start = 0x1000
        decoder.end = 0x1000 + 64
        
        # Create 8bpp test data
        gfx_8bpp_data = bytearray(64)
        self.cart.data = gfx_8bpp_data
        
        # Test decoding
        result = decoder.decode()
        
        self.assertIsInstance(result, str)
        self.assertIn('test_gfx_8bpp:', result)

    def test_tilemap_decoder(self):
        """Test tilemap decoder."""
        config = {
            'type': 'tilemap',
            'label': 'test_tilemap',
            'start': 0x1000,
            'end': 0x1000 + len(self.tilemap_data),
            'width': 4,
            'tilesize': '8x8'
        }
        
        decoder = TileMapDecoder(self.cart, config)
        decoder.start = 0x1000
        decoder.end = 0x1000 + len(self.tilemap_data)
        
        # Mock cartridge data
        self.cart.data = self.tilemap_data
        
        # Test decoding
        result = decoder.decode()
        
        self.assertIsInstance(result, str)
        self.assertIn('test_tilemap:', result)

    def test_array_decoder_8bit(self):
        """Test array decoder with 8-bit elements."""
        config = {
            'type': 'array',
            'label': 'test_array_8bit',
            'start': 0x1000,
            'end': 0x1000 + len(self.array_data),
            'size': 1
        }
        
        decoder = ArrayDecoder(self.cart, config)
        decoder.start = 0x1000
        decoder.end = 0x1000 + len(self.array_data)
        
        # Mock cartridge data
        self.cart.data = self.array_data
        
        # Test decoding
        result = decoder.decode()
        
        self.assertIsInstance(result, str)
        self.assertIn('test_array_8bit:', result)

    def test_array_decoder_16bit(self):
        """Test array decoder with 16-bit elements."""
        config = {
            'type': 'array',
            'label': 'test_array_16bit',
            'start': 0x1000,
            'end': 0x1000 + 8,  # 4 elements * 2 bytes
            'size': 2
        }
        
        decoder = ArrayDecoder(self.cart, config)
        decoder.start = 0x1000
        decoder.end = 0x1000 + 8
        
        # Create 16-bit test data
        array_16bit_data = bytearray([0x10, 0x20, 0x30, 0x40, 0x50, 0x60, 0x70, 0x80])
        self.cart.data = array_16bit_data
        
        # Test decoding
        result = decoder.decode()
        
        self.assertIsInstance(result, str)
        self.assertIn('test_array_16bit:', result)

    def test_array_decoder_with_struct(self):
        """Test array decoder with struct configuration."""
        config = {
            'type': 'array',
            'label': 'test_array_struct',
            'start': 0x1000,
            'end': 0x1000 + 8,  # 2 elements * 4 bytes each
            'struct': {
                'hp': 1,
                'attack': 1,
                'defense': 1,
                'flags': 1
            }
        }
        
        decoder = ArrayDecoder(self.cart, config)
        decoder.start = 0x1000
        decoder.end = 0x1000 + 8
        
        # Create struct test data
        struct_data = bytearray([10, 5, 8, 0x01, 20, 12, 15, 0x02])
        self.cart.data = struct_data
        
        # Test decoding
        result = decoder.decode()
        
        self.assertIsInstance(result, str)
        self.assertIn('test_array_struct:', result)

    def test_struct_decoder(self):
        """Test struct decoder."""
        config = {
            'type': 'struct',
            'label': 'test_struct',
            'start': 0x1000,
            'end': 0x1000 + 4,  # Single 4-byte struct
            'count': 1,
            'fields': {
                'x_pos': 1,
                'y_pos': 1,
                'tile_id': 2
            }
        }
        
        decoder = StructDecoder(self.cart, config)
        decoder.start = 0x1000
        decoder.end = 0x1000 + 4
        
        # Create struct test data
        struct_data = bytearray([100, 50, 0x34, 0x12])  # x=100, y=50, tile_id=0x1234
        self.cart.data = struct_data
        
        # Test decoding
        result = decoder.decode()
        
        self.assertIsInstance(result, str)
        self.assertIn('test_struct:', result)

    def test_struct_decoder_with_bitfields(self):
        """Test struct decoder with bitfield configuration."""
        config = {
            'type': 'struct',
            'label': 'test_struct_bitfields',
            'start': 0x1000,
            'end': 0x1000 + 4,  # Single 4-byte struct
            'count': 1,
            'fields': {
                'x_pos': 1,
                'flags': {
                    'size': 2,
                    'bitfields': {
                        'tile_id': {'bits': '0-9', 'mask': 0x03FF},
                        'palette': {'bits': '10-12', 'mask': 0x1C00, 'shift': 10},
                        'priority': {'bit': 14},
                        'flip': {'bit': 15}
                    }
                }
            }
        }
        
        decoder = StructDecoder(self.cart, config)
        decoder.start = 0x1000
        decoder.end = 0x1000 + 4
        
        # Create bitfield test data
        bitfield_data = bytearray([100, 0x34, 0x12, 0x00])
        self.cart.data = bitfield_data
        
        # Test decoding
        result = decoder.decode()
        
        self.assertIsInstance(result, str)
        self.assertIn('test_struct_bitfields:', result)

    def test_index_decoder(self):
        """Test index/pointer table decoder."""
        config = {
            'type': 'index',
            'label': 'test_index',
            'start': 0x1000,
            'end': 0x1000 + len(self.index_data),
            'size': 2
        }
        
        # Mock label lookup
        mock_disasm = MagicMock()
        mock_disasm.get_label.side_effect = lambda addr: {
            0x8000: 'label_8000',
            0x8020: 'label_8020',
            0x8040: 'label_8040'
        }.get(addr, None)
        
        decoder = IndexDecoder(self.cart, config, mock_disasm)
        decoder.start = 0x1000
        decoder.end = 0x1000 + len(self.index_data)
        
        # Mock cartridge data and address translation
        self.cart.data = self.index_data
        self.cart.address.side_effect = lambda x: 0x8000 + (x - 0x1000)
        
        # Test decoding
        result = decoder.decode()
        
        self.assertIsInstance(result, str)
        self.assertIn('test_index:', result)

    def test_text_decoder(self):
        """Test text decoder."""
        # Create translation table
        translation_table = {
            'type': 'translation',
            'label': 'test_translation',
            'table': {
                0x41: 'A',
                0x42: 'B', 
                0x43: 'C',
                0x00: ''
            }
        }
        
        config = {
            'type': 'text',
            'label': 'test_text',
            'start': 0x1000,
            'end': 0x1000 + len(self.text_data),
            'translation': 'test_translation'
        }
        
        # Mock configurator with translation table
        mock_config = MagicMock(spec=Configurator)
        mock_config.get.return_value = [translation_table]
        
        decoder = TextDecoder(self.cart, config, mock_config)
        decoder.start = 0x1000
        decoder.end = 0x1000 + len(self.text_data)
        
        # Mock cartridge data
        self.cart.data = self.text_data
        
        # Test decoding
        result = decoder.decode()
        
        self.assertIsInstance(result, str)
        self.assertIn('test_text:', result)

    def test_sound_decoder(self):
        """Test sound/BRR decoder."""
        config = {
            'type': 'sound',
            'label': 'test_sound',
            'start': 0x1000,
            'end': 0x1000 + len(self.brr_data)
        }
        
        decoder = SoundDecoder(self.cart, config)
        decoder.start = 0x1000
        decoder.end = 0x1000 + len(self.brr_data)
        
        # Mock cartridge data
        self.cart.data = self.brr_data
        
        # Test decoding
        result = decoder.decode()
        
        self.assertIsInstance(result, str)
        self.assertIn('test_sound:', result)

    def test_data_decoder(self):
        """Test raw data decoder."""
        config = {
            'type': 'data',
            'label': 'test_data',
            'start': 0x1000,
            'end': 0x1000 + 16
        }
        
        decoder = DataDecoder(self.cart, config)
        decoder.start = 0x1000
        decoder.end = 0x1000 + 16
        
        # Create test data
        data_bytes = bytearray([0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88,
                               0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x00])
        self.cart.data = data_bytes
        
        # Test decoding
        result = decoder.decode()
        
        self.assertIsInstance(result, str)
        self.assertIn('test_data:', result)
        self.assertIn('.db', result)

    def test_binary_decoder(self):
        """Test binary file decoder."""
        config = {
            'type': 'bin',
            'label': 'test_binary',
            'start': 0x1000,
            'end': 0x1000 + 32
        }
        
        decoder = BinaryDecoder(self.cart, config)
        decoder.start = 0x1000
        decoder.end = 0x1000 + 32
        
        # Create test data
        binary_data = bytearray(32)
        self.cart.data = binary_data
        
        # Test decoding
        result = decoder.decode()
        
        self.assertIsInstance(result, str)
        self.assertIn('test_binary:', result)
        self.assertIn('.INCBIN', result)

    def test_decoder_factory(self):
        """Test decoder factory function."""
        # Test all supported decoder types
        decoder_types = [
            ('data', DataDecoder),
            ('bin', BinaryDecoder),
            ('gfx', GraphicDecoder),
            ('palette', PaletteDecoder),
            ('tilemap', TileMapDecoder),
            ('array', ArrayDecoder),
            ('struct', StructDecoder),
            ('index', IndexDecoder),
            ('text', TextDecoder),
            ('sound', SoundDecoder),
        ]
        
        for dtype, expected_class in decoder_types:
            config = {
                'type': dtype,
                'label': f'test_{dtype}',
                'start': 0x1000,
                'end': 0x1000 + 16
            }
            
            decoder = DecoderFactory.create(self.cart, config)
            self.assertIsInstance(decoder, expected_class)

    def test_decoder_with_compression(self):
        """Test decoder with compression parameter."""
        config = {
            'type': 'data',
            'label': 'test_compressed',
            'start': 0x1000,
            'end': 0x1000 + 16,
            'compress': 'lz2'
        }
        
        decoder = DataDecoder(self.cart, config)
        self.assertEqual(decoder.compress, 'lz2')

    def test_decoder_address_translation(self):
        """Test that decoders properly handle address translation."""
        config = {
            'type': 'data',
            'label': 'test_addresses',
            'start': 0x1000,
            'end': 0x1000 + 4
        }
        
        decoder = DataDecoder(self.cart, config)
        decoder.start = 0x1000
        decoder.end = 0x1000 + 4
        
        # Mock address translation
        self.cart.address.side_effect = lambda x: 0x8000 + (x - 0x1000)
        self.cart.data = bytearray([0x11, 0x22, 0x33, 0x44])
        
        # Test decoding
        result = decoder.decode()
        
        # Should handle address translation correctly
        self.assertIsInstance(result, str)

    def test_decoder_error_handling(self):
        """Test decoder error handling for invalid configurations."""
        # Test with empty data
        config = {
            'type': 'data',
            'label': 'test_empty',
            'start': 0x1000,
            'end': 0x1000  # No data
        }
        
        decoder = DataDecoder(self.cart, config)
        decoder.start = 0x1000
        decoder.end = 0x1000
        
        self.cart.data = bytearray()
        
        # Should handle empty data gracefully
        result = decoder.decode()
        self.assertIsInstance(result, str)

    def test_graphics_decoder_palette_reference(self):
        """Test graphics decoder with palette reference."""
        config = {
            'type': 'gfx',
            'label': 'test_gfx_pal',
            'start': 0x1000,
            'end': 0x1000 + len(self.gfx_4bpp_data),
            'bit_depth': 4,
            'palette': 'test_palette_ref'
        }
        
        decoder = GraphicDecoder(self.cart, config)
        self.assertEqual(decoder.palette, 'test_palette_ref')

    def test_mode7_graphics_decoder(self):
        """Test Mode7 graphics decoder."""
        config = {
            'type': 'gfx',
            'label': 'test_mode7',
            'start': 0x1000,
            'end': 0x1000 + 128,  # Mode7 tile data
            'bit_depth': 'mode7'
        }
        
        decoder = GraphicDecoder(self.cart, config)
        self.assertEqual(decoder.bit_depth, 'mode7')
        
        # Create Mode7 test data
        mode7_data = bytearray(128)
        self.cart.data = mode7_data
        
        decoder.start = 0x1000
        decoder.end = 0x1000 + 128
        
        # Test decoding
        result = decoder.decode()
        
        self.assertIsInstance(result, str)
        self.assertIn('test_mode7:', result)


if __name__ == '__main__':
    unittest.main()