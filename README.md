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
* Code path tracing to statically analyze instructions and automatically generate labels
* LoROM, HiROM with fast and slow ROM detection.
* Extract and edit game assets like graphics, palettes and tile-maps.
* SPC700 audio processor disassembly support with nested decoders for embedded data.
* SNES register symbol detection with code commentary.
* Support for arrays, indices, structured data with bitfields, and encoded text.
* Automatic label lookup in index tables for readable assembly output.
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

Here is an example of a basic YAML configuration file.
```yaml
---
# ROM label addresses for code and generic data
labels:
  snesinit: 0x2
# Memory address locations
memory:
  lives: 0x60
  snes_joypad_state: 0x7E2008
# Structured data for decoding
decoders:
- type: data
  label: hdmaGradient0List0
  start: 0x8A00
  end: 0x8B00
```

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

### decoders:
List of decoder definitions and their base parameters. 

| Parameter | Example | Description |
|-----------|---------|-------------|
| **type** | data | Type of decoder (see Decoder Types below) |
| **label** | gradient1 | Unique name for code label |
| **start** | 0x2fa90 | ROM offset where data begins (hexadecimal) |
| **end** | 0x2faf0 | ROM offset where data ends (hexadecimal) |
| **compress** | lz2 | Optional compression algorithm (see Compression Support) |
| **(options)** | - | Decoder-specific options (see below) |

#### Decoder Types:
- **data** - Raw data bytes (basic .db directives)
- **bin** - Binary data files (outputs as .INCBIN directive)
- **gfx** - SNES graphics/tiles (2bpp, 3bpp, 4bpp, 8bpp, Mode7)
- **palette** - SNES color palettes (15-bit BGR)
- **tilemap** - Tilemap data with various tile sizes
- **array** - Structured data arrays with configurable element size or struct fields
- **struct** - Structured data with named fields and bitfield support
- **index** - Index/pointer tables with automatic label lookup
- **text** - Encoded text with translation tables
- **translation** - Character translation tables for text decoding
- **spc700** - SPC700 audio processor code (generates .spc assembly file)
- **sound** - BRR audio samples (SNES audio format)
  
#### Graphics Decoder:
| Parameter | Example | Description |
|--------|---------|-------------|
| **bit_depth** | 4 | Bits per pixel (2, 3, 4, 8, or "mode7") |
| **palette** | sprite_pal | Reference to palette decoder label. The palette must be sequentially defined first before refencing it. |
| **width** | 128 | Image width in pixels (optional, for PNG output) |

Graphics example:
```yaml
decoders:
  # Extract graphics with palette reference
  - type: gfx
    label: sprites1_gfx
    start: 0x2bc60
    end: 0x2c860
    bit_depth: 4
    palette: sprites1_pal
```

#### Palette Decoder:
A palette decoder defines an array of 15-bit BGR565 colors which can be referenced by other graphic decoders.

Palette example:
```yaml
decoders:
  # Extract palette
  - type: palette
    label: sprites1_pal
    start: 0x2f940
    end: 0x2f960
```

#### Tilemap Decoder:
| Parameter | Example | Description |
|--------------|---------|-------------|
| **tilesize** | 8x8 | Tile dimensions (8x8, 16x16, 32x32, etc.) |
| **gfx**      | sprites1_gfx | Reference to a graphic decoder label used by this tilemap |
| **width**    | 32 | Tilemap width in tiles |

Tilemap example:
```yaml
decoders:
  - type: tilemap
    label: bg_tiles_level1
    start: 0x2f940
    end: 0x2f960

  - type: tilemap
    label: bg_tiles_level1
    start: 0x46000
    end: 0x46800
    width: 32
    gfx: sprites1_gfx
```

#### Array Decoder:
| Parameter | Example | Description |
|--------|---------|-------------|
| **size** | 2 | Size of each array element in bytes (1, 2, 3, or 4) |
| **struct** | {hp: 1, attack: 1} | Structured fields with named elements (see Struct Decoder) |
| **index** | {start: 0x1000, end: 0x1010, size: 2} | Index table for variable-positioned array elements |

Array Example:
```yaml
decoders:
  # Basic array of 16-bit integers with 256 elements
  - type: array
    label: enemy_stats
    start: 0x1000
    end: 0x1200
    size: 2

  # Array with structured fields
  - type: array
    label: enemy_stats
    start: 0x30000
    end: 0x30028  # 4 enemies * 10 bytes each
    struct:
      hp: 1
      attack: 1
      defense: 1
      sprite_id: 2
      ai_type: 1
      flags:
        size: 2
        bitfields:
          can_fly: {bit: 0}
          is_boss: {bit: 1}
          palette: {bits: "2-4", mask: 0x001C, shift: 2}
      drop_item: 2
```

#### Struct Decoder:
| Parameter | Example | Description |
|--------|---------|-------------|
| **fields** | {width: 1, height: 1} | Named fields with sizes (1-4 bytes each) |
| **count** | 10 | Number of struct instances (optional, auto-calculated from size) |

**Field Types:**
- **Simple fields**: `field_name: size_in_bytes` (e.g., `hp: 1`, `tileset_id: 2`)
- **Bitfield fields**: Bit-packed data with sub-fields extracted using masks and shifts

Struct Example:
```yaml
decoders:
  # Standalone struct decoder for level headers
  - type: struct
    label: level_headers
    start: 0x40000
    end: 0x40020
    count: 4  # 4 levels
    fields:
      width: 1
      height: 1
      tileset_id: 2
      music_id: 1
      bg_color:
        size: 2
        bitfields:
          red: {bits: "0-4", mask: 0x001F}
          green: {bits: "5-9", mask: 0x03E0, shift: 5}
          blue: {bits: "10-14", mask: 0x7C00, shift: 10}
```

**Bitfield Syntax:**
```yaml
field_name:
  size: 2  # Total field size in bytes
  bitfields:
    subfield1: {bits: "0-9", mask: 0x03FF}           # Bit range
    subfield2: {bit: 10}                             # Single bit
    subfield3: {bits: "12-14", mask: 0x7000, shift: 12}  # With custom shift
```

**Generated output for bitfields:**
This generates editable expressions that WLA-DX assembles into the correct bit-packed value.
```asm
.dw ($042 << 0) | (1 << 10) | (7 << 12)  ; field_name: subfield1=$042 subfield2=1 subfield3=7
```

#### Index Decoder:
| Parameter | Example | Description |
|-----------|---------|-------------|
| **size** | 2 | Size of each pointer/offset in bytes (1, 2, 3, or 4) |

**Automatic Label Lookup:**
IndexDecoder automatically looks up labels for decoded pointer values. When a decoded address matches a label defined in the `labels:` section, it outputs the label name instead of a hex value:

Index example:
```yaml
labels:
  music_game_start: 0xA020
  music_game_end:   0xA040
decoders:
  # Index table with automatic label lookup
  - type: index
    label: music_table
    start: 0x50000
    end: 0x50006  # 3 entries * 2 bytes
    size: 2
```
Index assembly output:
```asm
music_table:
music_table_0:
    .dw music_game_start  ; Address matched label
music_table_1:
    .dw music_game_end    ; Address matched label
music_table_2:
    .dw $7FFF             ; No label, uses hex
```

#### Text Decoder:
| Parameter | Example | Description |
|-----------|---------|-------------|
| **translation** | default | Reference to translation table decoder label |

```yaml
- type: text
  label: dialog1_text
  start: 0x80400
  end: 0x88000
  translation: default
  index:
    start: 0x80000
    end: 0x80400
```

#### Translation Decoder:
| Parameter | Example  | Description |
|-----------|----------|-------------|
| **table** | 0x0: "A" | Mapping of integers to strings |

A meta data entity which defines how to translate a set of numbers to strings. 

```yaml
decoders: 
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
```

#### SPC700 Decoder:
| Parameter | Example | Description |
|-----------|---------|-------------|
| **start_addr** | 0x0200 | SPC700 memory load address (optional, default: 0x0000) |
| **labels** | {0x0000: main} | SPC700-specific labels as offset:name pairs (optional) |
| **decoders** | [...] | Nested decoders for data within SPC700 code (optional) |

SPC700 example:
```yaml
decoders:
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
```

**Nested Decoders:**
The SPC700 decoder supports nested decoders to extract data embedded within the audio code. This allows you to identify and label data tables, arrays, sound samples, and other assets that are part of the SPC700 program. Nested decoder offsets are relative to the start of the SPC700 data (not ROM addresses).

Allowed nested decoder types:
- **data** - Raw data bytes
- **bin** - Binary data (outputs as .INCBIN)
- **array** - Structured data arrays
- **index** - Index/pointer tables
- **sound** - BRR audio samples

#### Sound Decoder:
Sound example:

```yaml
  # Extract BRR audio sample
  - type: sound
    label: sample_brr
    start: 0x20800
    end: 0x20B84
```

### Example Decoders YAML

```yaml
---
# Define decoders to extract assets
decoders:
  # Extract palette (must come before gfx that reference it)
  - type: palette
    label: sprites1_pal
    start: 0x2f940
    end: 0x2f960

  # Extract BRR audio sample
  - type: sound
    label: sample_brr
    start: 0x20800
    end: 0x20B84

```
### banks:
You can explictly specify the bank numbers in a ROM that contain executable code. Other banks will be disassembled as data only. Generally it's better not to use this unless you are certain the banks that contain code. Omitting the banks option will allow for automatic code tracing.  

```yaml
banks: [0, 1, 2, 3, 4, 5, 8]
```


## Compression Support

SNES2ASM supports automatic decompression and recompression of data for decoders. Supported algorithms:

- **aplib** - aPLib compression
- **byte_rle** - Byte-based run-length encoding
- **rle1, rle2** - Run-length encoding variants
- **lz1, lz2, lz3, lz4, lz5** - LZ compression variants
- **lz19** - LZ-based compression

For this example we have a tilemap that is encoded using the `lz3` compression algorithms. Any decoder type can utilize compression encoding / decoding.
```yaml
decoders:
  - type: tilemap
    label: map1
    compress: lz3
    tilesize: 8x8
    width: 32
    start: 0x137AB
    end: 0x139B7
```

Specify compression using the `compress` parameter in any decoder.

## Sample ROM

If documentation makes you bored, try the provided sample! Seeing is believing.

```bash
snes2asm -c snes2asm/tests/classickong.yaml -o classickong snes2asm/tests/classickong.smc
cd classickong
make
```
