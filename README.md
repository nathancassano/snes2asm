SNES2ASM
========

Overview
--------

SNES2ASM is more than a disassembler. Generate assembly code with insights! Control the pipelines to assets like graphics, tile-maps, palettes and text. Write your own configuration files describing the layouts of your ROMS. Makes developing your game modifications easy than ever.

### Features
* Complete ROM disassembly and reassembly.
* LoROM, HiROM with fast and slow ROM detection.
* Extract and edit game assets like graphics, palettes and tile-maps.
* Advanced code path detection and label generation.
* SNES register symbol detection with code commentary.
* Custom configuration of game disassembly.


Installation
------------

Clone this repo onto your computer, then:
```
    cd snes2asm
    sudo python setup.py install
```

Requirements
------------

  For compiling the output project you will need.

  * WLA DX Assembler - https://github.com/vhelin/wla-dx
  * GNU Make

Usage
-----
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
### Running:
```
snes2asm -b 0 1 -o output_dir snes2asm/tests/classickong.smc
```

Project Assembly
----------------
Once successfully disassembling your ROM into a project folder the next step is to test compilation.
```
    cd output_dir
    # Edit Makefile PREFIX for the wlx-da install path
    make
    # Done! Next run output_dir/game.smc file is your emulator.
```

Configuration
-------------

In addition to decompiling assembly code other data assets such as graphics, tilemaps and text can be decoded by specifying a YAML configuration file.

### banks:
An array of bank numbers in the rom that hold machine code. Other banks will only be disassembled as data.
```
[0,1,2,3,4,5,8]
```
### decoders:
List of decoder objects and their parameters.
| - | Example | Description
|--|--|--|
| **label:** | gradient1 | Unique name for code label 
| **type:** | data | Type of decoder being used (data,gfx,palette)
| **start:** | 0x2fa90 | Hex address of starting point 
| **end:** | 0x2faf0 | Hex address of ending point 
| **(options):** | * | Other specific decoder options

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

**Example YAML configuration:**
```
---
banks: [0,3,4,5,7]
decoders:
- type: palette
  label: sprites1_pal
  start: 0x2f940
  end: 0x2f960
- type: gfx
  label: sprites1_gfx
  start: 0x2bc60
  end: 0x2c860
  bit_depth: 4
  palette: sprites1_pal
- type: translation
  label: default
  table:
    0x0: "A"
    0x1: "B"
    0x2: "Long string"
- type: text
  label: dialog
  translation: default
  start: 0x10000
  end: 0x10010
labels:
  read_joy: 0x182EC
  draw_oam: 0x13983
memory:
  health: 0x701011
  lives: 0xDAA7
```


Sample ROM
==========
If documenation makes you bored then try the provided sample! Seeing is believing. 
```
snes2asm -c snes2asm/tests/classickong.yaml -o classickong snes2asm/tests/classickong.smc
cd classickong
make
```
