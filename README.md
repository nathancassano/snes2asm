SNES2ASM
========

A powerful SNES ROM disassembler that generates reassemblable assembly projects with full asset extraction support.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Requirements](#requirements)
- [Usage](#usage)
- [Configuration](#configuration)
- [Compression Support](#compression-support)
- [Sample ROM](#sample-rom)

## Overview

SNES2ASM is more than a disassembler. Generate assembly code with insights! Control the pipelines to assets like graphics, tile-maps, palettes, sound and text. Write your own configuration files describing the layouts of your ROMs. Makes developing your game modifications easier than ever.

### Features
* Complete ROM disassembly and reassembly.
* LoROM, HiROM with fast and slow ROM detection.
* Extract and edit game assets like graphics, palettes and tile-maps.
* SPC700 audio processor disassembly support with nested decoders for embedded data.
* Advanced code path detection and label generation.
* SNES register symbol detection with code commentary.
* Support for arrays, indices and encoded text.
* Integrated data decompression and recompression.
* Custom configuration of game disassembly.

## Quick Start

```bash
# 1. Install
cd snes2asm
sudo python setup.py install

# 2. Basic disassembly
snes2asm -o my_project rom.sfc

# 3. Build the project
cd my_project
make

# 4. Test in your emulator
# Output is my_project/game.smc
```

For advanced usage with asset extraction, create a YAML config file (see [Configuration](#configuration)).

## Installation

Clone this repository and install:

```bash
cd snes2asm
sudo python setup.py install
```

## Requirements

For compiling the output project you will need:

* **WLA-DX Assembler** - https://github.com/vhelin/wla-dx
* **GNU Make**

## Usage
Provided is a command line interface tool `snes2asm` with the following options.
```
usage: snes2asm [-h] [-v] [-o OUTPUT_DIR] [-c CONFIG] [-b BANKS [BANKS ...]]
                [-hi] [-lo] [-f] [-s] [-nl] [-x] snes.sfc

Disassembles snes cartridges into practical projects

positional arguments:
  snes.sfc              input snes file

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Verbose output
  -o OUTPUT_DIR, --output_dir OUTPUT_DIR
                        File path to output project
  -c CONFIG, --config CONFIG
                        Path to decoding configuration yaml file
  -b BANKS [BANKS ...], --banks BANKS [BANKS ...]
                        Code banks to disassemble. Default is auto-detect
  -hi, --hirom          Force HiROM
  -lo, --lorom          Force LoROM
  -f, --fastrom         Force fast ROM addressing
  -s, --slowrom         Force slow ROM addressing
  -nl, --nolabel        Use addresses instead of labels
  -x, --hex             Comments show instruction hex
```

### Example Usage:
```bash
snes2asm -b 0 1 -o output_dir snes2asm/tests/classickong.smc
```

## Project Assembly

Once successfully disassembling your ROM into a project folder, the next step is to test compilation.

```bash
cd output_dir
# Edit Makefile PREFIX to point to your wla-dx install path
make
# Done! Run the output_dir/game.smc file in your emulator.
```

### Output Structure

The disassembler creates the following project structure:

```
output_dir/
├── Makefile              # Build configuration
├── bank_00.asm           # Bank 0 assembly code
├── bank_01.asm           # Bank 1 assembly code
├── ...                   # Additional banks
├── sprites1_gfx.chr      # Extracted graphics
├── sprites1_gfx.png      # PNG preview (if palette provided)
├── sprites1_pal.pal      # Extracted palettes
├── spc700.S              # SPC700 assembly (if configured)
└── game.smc              # Reassembled ROM (after make)
```

## Configuration

In addition to disassembling executable code, data assets such as graphics, tilemaps, palettes, audio, and text can be extracted by specifying a YAML configuration file.

### banks:
An array of bank numbers in the ROM that contain executable code. Other banks will only be disassembled as data.

```yaml
banks: [0, 1, 2, 3, 4, 5, 8]
```
### decoders:
List of decoder objects and their parameters.

| Parameter | Example | Description |
|-----------|---------|-------------|
| **label** | gradient1 | Unique name for code label |
| **type** | data | Type of decoder (see Decoder Types below) |
| **start** | 0x2fa90 | ROM offset where data begins (hexadecimal) |
| **end** | 0x2faf0 | ROM offset where data ends (hexadecimal) |
| **compress** | lz2 | Optional compression algorithm (see Compression Support) |
| **(options)** | - | Decoder-specific options (see below) |

#### Decoder Types:
- **data** - Raw data bytes (basic .db directives)
- **gfx** - SNES graphics/tiles (2bpp, 3bpp, 4bpp, 8bpp, Mode7)
- **palette** - SNES color palettes (15-bit RGB)
- **spc700** - SPC700 audio processor code (generates .spc assembly file)
- **sound** - BRR audio samples (SNES audio format)
- **text** - Encoded text with translation tables
- **tilemap** - Tilemap data with various tile sizes
- **array** - Structured data arrays with configurable element size
- **bin** - Binary data (outputs as .INCBIN directive)
- **translation** - Character translation tables for text decoding
- **index** - Index/pointer tables

#### Graphics Decoder Options:
| Option | Example | Description |
|--------|---------|-------------|
| **bit_depth** | 4 | Bits per pixel (2, 3, 4, 8, or "mode7") |
| **palette** | sprite_pal | Reference to palette decoder label |
| **width** | 128 | Image width in pixels (optional, for PNG output) |

#### Tilemap Decoder Options:
| Option | Example | Description |
|--------|---------|-------------|
| **tilesize** | 8x8 | Tile dimensions (8x8, 16x16, 32x32, etc.) |
| **width** | 32 | Tilemap width in tiles |

#### Array Decoder Options:
| Option | Example | Description |
|--------|---------|-------------|
| **size** | 2 | Size of each array element in bytes (1, 2, 3, or 4) |

#### Text Decoder Options:
| Option | Example | Description |
|--------|---------|-------------|
| **translation** | default | Reference to translation table decoder label |

#### SPC700 Decoder Options:
| Option | Example | Description |
|--------|---------|-------------|
| **start_addr** | 0x0200 | SPC700 memory load address (optional, default: 0x0000) |
| **labels** | {0x0000: main} | SPC700-specific labels as offset:name pairs (optional) |
| **decoders** | [...] | Nested decoders for data within SPC700 code (optional) |

**Nested Decoders:**
The SPC700 decoder supports nested decoders to extract data embedded within the audio code. This allows you to identify and label data tables, arrays, sound samples, and other assets that are part of the SPC700 program. Nested decoder offsets are relative to the start of the SPC700 data (not ROM addresses).

Allowed nested decoder types:
- **data** - Raw data bytes
- **bin** - Binary data (outputs as .INCBIN)
- **array** - Structured data arrays
- **index** - Index/pointer tables
- **sound** - BRR audio samples

### labels:
Set of value key pairs which maps a code address to a named label.
| Label | ROM Address
|--|--|
| **read_joy:** | 0x182EC |
| **draw_oam:** | 0x13983 |

### memory:
Set of value key pairs which maps a memory address to a named symbol.
| Symbol | Memory Address
|--|--|
| **health:** | 0x701011 |
| **lives:** | 0xDAA7 |

### structs:
-- TODO

### Example YAML Configuration

```yaml
---
# Specify which banks contain executable code
banks: [0, 3, 4, 5, 7]

# Define decoders to extract assets
decoders:
  # Extract palette (must come before gfx that reference it)
  - type: palette
    label: sprites1_pal
    start: 0x2f940
    end: 0x2f960

  # Extract graphics with palette reference
  - type: gfx
    label: sprites1_gfx
    start: 0x2bc60
    end: 0x2c860
    bit_depth: 4
    palette: sprites1_pal

  # Define character translation table
  - type: translation
    label: default
    table:
      0x0: "A"
      0x1: "B"
      0x2: "Long string"

  # Extract text using translation table
  - type: text
    label: dialog
    translation: default
    start: 0x10000
    end: 0x10010

  # Extract compressed tilemap
  - type: tilemap
    label: map1
    compress: byte_rle
    tilesize: 8x8
    width: 32
    start: 0x137AB
    end: 0x139B7

  # Extract BRR audio sample
  - type: sound
    label: sample_brr
    start: 0x20800
    end: 0x20B84

  # Disassemble SPC700 audio driver with nested data
  - type: spc700
    label: audio_driver
    start: 0x20000
    end: 0x20533
    start_addr: 0x0200
    labels:
      0x0000: main
      0x0040: loop
      0x0100: handleInput
    decoders:
      - type: array
        label: divTable
        start: 0x390  # Relative to SPC700 start
        end: 0x410
        size: 2
      - type: array
        label: vibratoTable
        start: 0x410
        end: 0x510

# Define custom labels for specific addresses
labels:
  read_joy: 0x182EC     # Function at ROM offset
  draw_oam: 0x13983

# Define RAM/memory symbols
memory:
  health: 0x701011      # RAM address
  lives: 0xDAA7
```


## Compression Support

SNES2ASM supports automatic decompression and recompression of data. Supported algorithms:

- **aplib** - aPLib compression
- **byte_rle** - Byte-based run-length encoding
- **rle1, rle2** - Run-length encoding variants
- **lz1, lz2, lz3, lz4, lz5** - LZ compression variants
- **lz19** - LZ-based compression

Specify compression using the `compress` parameter in any decoder.

## Sample ROM

If documentation makes you bored, try the provided sample! Seeing is believing.

```bash
snes2asm -c snes2asm/tests/classickong.yaml -o classickong snes2asm/tests/classickong.smc
cd classickong
make
```
