# -*- coding: utf-8 -*-

import unittest
import os
import tempfile
from unittest.mock import patch, mock_open
import yaml
from snes2asm.configurator import Configurator


class ConfiguratorTest(unittest.TestCase):
    """Test YAML configuration parsing and validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_config = {
            'banks': [0, 1, 2],
            'labels': {
                'init': 0x8000,
                'main_loop': 0x8100,
                'nmi_handler': 0x8200
            },
            'memory': {
                'player_health': 0x7E0010,
                'current_level': 0x7E0012,
                'score': 0x7E0014
            },
            'decoders': [
                {
                    'type': 'palette',
                    'label': 'main_palette',
                    'start': 0x2F000,
                    'end': 0x2F020
                },
                {
                    'type': 'gfx',
                    'label': 'sprite_tiles',
                    'start': 0x30000,
                    'end': 0x31000,
                    'bit_depth': 4,
                    'palette': 'main_palette'
                },
                {
                    'type': 'array',
                    'label': 'enemy_data',
                    'start': 0x40000,
                    'end': 0x40020,
                    'struct': {
                        'hp': 1,
                        'attack': 1,
                        'defense': 1,
                        'sprite_id': 2
                    }
                }
            ]
        }

    def test_valid_config_parsing(self):
        """Test parsing of valid YAML configuration."""
        config_yaml = yaml.dump(self.test_config)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            configurator = Configurator('dummy_path.yaml')
            
        # Test basic properties
        self.assertEqual(configurator.config['banks'], [0, 1, 2])
        self.assertEqual(configurator.config['labels'], self.test_config['labels'])
        self.assertEqual(configurator.config['memory'], self.test_config['memory'])
        self.assertEqual(len(configurator.config['decoders']), 3)

    def test_empty_config(self):
        """Test handling of empty configuration."""
        with patch('builtins.open', mock_open(read_data='{}')):
            configurator = Configurator('dummy_path.yaml')
            self.assertEqual(configurator.config, {})

    def test_config_with_banks_only(self):
        """Test configuration with only banks specified."""
        config = {'banks': [0, 1, 2, 3]}
        config_yaml = yaml.dump(config)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            configurator = Configurator('dummy_path.yaml')
            
        self.assertEqual(configurator.config['banks'], [0, 1, 2, 3])

    def test_config_with_labels_only(self):
        """Test configuration with only labels specified."""
        config = {
            'labels': {
                'start': 0x8000,
                'update': 0x8100
            }
        }
        config_yaml = yaml.dump(config)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            configurator = Configurator('dummy_path.yaml')
            
        self.assertEqual(configurator.config['labels'], config['labels'])

    def test_config_with_memory_only(self):
        """Test configuration with only memory symbols specified."""
        config = {
            'memory': {
                'lives': 0x7E0000,
                'score': 0x7E0002
            }
        }
        config_yaml = yaml.dump(config)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            configurator = Configurator('dummy_path.yaml')
            
        self.assertEqual(configurator.config['memory'], config['memory'])

    def test_memory_validation_removes_invalid_addresses(self):
        """Test that memory symbols with invalid addresses are removed."""
        config = {
            'memory': {
                'valid_low': 0x1000,      # Should be kept
                'valid_high': 0x7F0000,   # Should be kept  
                'invalid_mid1': 0x3000,   # Should be removed (2000-7E0000 range)
                'invalid_mid2': 0x7D0000  # Should be removed (2000-7E0000 range)
            }
        }
        config_yaml = yaml.dump(config)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            configurator = Configurator('dummy_path.yaml')
            
        memory = configurator.config['memory']
        self.assertIn('valid_low', memory)
        self.assertIn('valid_high', memory)
        self.assertNotIn('invalid_mid1', memory)
        self.assertNotIn('invalid_mid2', memory)

    def test_decoder_validation(self):
        """Test decoder configuration validation."""
        # Test all supported decoder types
        decoder_types = [
            'data', 'bin', 'gfx', 'palette', 'tilemap',
            'array', 'struct', 'index', 'text', 'translation',
            'spc700', 'sound'
        ]
        
        config = {
            'decoders': [
                {'type': dtype, 'label': f'test_{dtype}', 'start': 0x1000, 'end': 0x2000}
                for dtype in decoder_types
            ]
        }
        config_yaml = yaml.dump(config)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            configurator = Configurator('dummy_path.yaml')
            
        decoders = configurator.config['decoders']
        self.assertEqual(len(decoders), len(decoder_types))
        
        for decoder in decoders:
            self.assertIn(decoder['type'], decoder_types)

    def test_decoder_with_compression(self):
        """Test decoder configuration with compression."""
        config = {
            'decoders': [
                {
                    'type': 'gfx',
                    'label': 'compressed_tiles',
                    'start': 0x10000,
                    'end': 0x11000,
                    'compress': 'lz2'
                }
            ]
        }
        config_yaml = yaml.dump(config)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            configurator = Configurator('dummy_path.yaml')
            
        decoder = configurator.config['decoders'][0]
        self.assertEqual(decoder['compress'], 'lz2')

    def test_struct_decoder_with_bitfields(self):
        """Test struct decoder with bitfield configuration."""
        config = {
            'decoders': [
                {
                    'type': 'struct',
                    'label': 'sprite_data',
                    'start': 0x1000,
                    'end': 0x1008,
                    'fields': {
                        'x_pos': 1,
                        'y_pos': 1,
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
            ]
        }
        config_yaml = yaml.dump(config)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            configurator = Configurator('dummy_path.yaml')
            
        decoder = configurator.config['decoders'][0]
        flags_field = decoder['fields']['flags']
        self.assertEqual(flags_field['size'], 2)
        self.assertIn('bitfields', flags_field)
        self.assertEqual(len(flags_field['bitfields']), 4)

    def test_spc700_decoder_with_nested_decoders(self):
        """Test SPC700 decoder with nested decoders."""
        config = {
            'decoders': [
                {
                    'type': 'spc700',
                    'label': 'audio_driver',
                    'start': 0x20000,
                    'end': 0x20500,
                    'start_addr': 0x0200,
                    'labels': {
                        0x0000: 'main',
                        0x0040: 'loop',
                        0x0080: 'fade_out'
                    },
                    'decoders': [
                        {
                            'type': 'array',
                            'label': 'pitch_table',
                            'start': 0x100,
                            'end': 0x200,
                            'size': 2
                        },
                        {
                            'type': 'sound',
                            'label': 'drum_sample',
                            'start': 0x300,
                            'end': 0x400
                        }
                    ]
                }
            ]
        }
        config_yaml = yaml.dump(config)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            configurator = Configurator('dummy_path.yaml')
            
        decoder = configurator.config['decoders'][0]
        self.assertEqual(decoder['type'], 'spc700')
        self.assertEqual(decoder['start_addr'], 0x0200)
        self.assertEqual(len(decoder['labels']), 3)
        self.assertEqual(len(decoder['decoders']), 2)

    def test_graphics_decoder_with_palette_reference(self):
        """Test graphics decoder that references a palette."""
        config = {
            'decoders': [
                {
                    'type': 'palette',
                    'label': 'sprite_palette',
                    'start': 0x2F000,
                    'end': 0x2F020
                },
                {
                    'type': 'gfx',
                    'label': 'sprite_tiles',
                    'start': 0x30000,
                    'end': 0x31000,
                    'bit_depth': 4,
                    'palette': 'sprite_palette'
                }
            ]
        }
        config_yaml = yaml.dump(config)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            configurator = Configurator('dummy_path.yaml')
            
        decoders = configurator.config['decoders']
        self.assertEqual(len(decoders), 2)
        self.assertEqual(decoders[1]['palette'], 'sprite_palette')

    def test_file_not_found_error(self):
        """Test handling of missing configuration file."""
        with self.assertRaises(FileNotFoundError):
            Configurator('nonexistent_file.yaml')

    def test_invalid_yaml_syntax(self):
        """Test handling of invalid YAML syntax."""
        invalid_yaml = """
        decoders:
          - type: gfx
            label: test
            start: 0x1000
            end: 0x2000
            invalid_syntax: [unclosed array
        """
        
        with patch('builtins.open', mock_open(read_data=invalid_yaml)):
            with self.assertRaises(yaml.YAMLError):
                Configurator('dummy_path.yaml')

    def test_config_direct_access(self):
        """Test direct access to config dictionary."""
        config_yaml = yaml.dump({'banks': [0, 1]})
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            configurator = Configurator('dummy_path.yaml')
            
        # Test direct config access
        self.assertEqual(configurator.config['banks'], [0, 1])
        
        # Test missing key with direct access
        with self.assertRaises(KeyError):
            _ = configurator.config['nonexistent']

    def test_complete_example_config(self):
        """Test parsing of a complete example configuration."""
        config_yaml = yaml.dump(self.test_config)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            configurator = Configurator('dummy_path.yaml')
            
        # Verify all sections are present
        self.assertIn('banks', configurator.config)
        self.assertIn('labels', configurator.config)
        self.assertIn('memory', configurator.config)
        self.assertIn('decoders', configurator.config)
        
        # Verify decoder types
        decoder_types = [d['type'] for d in configurator.config['decoders']]
        expected_types = ['palette', 'gfx', 'array']
        self.assertEqual(decoder_types, expected_types)


if __name__ == '__main__':
    unittest.main()