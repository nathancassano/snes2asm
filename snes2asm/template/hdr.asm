.MEMORYMAP                      ; Begin describing the system architecture.
  SLOTSIZE $8000                ; The slot is $8000 bytes in size. More details on slots later.
  DEFAULTSLOT 0                 ; There's only 1 slot in SNES, there are more in other consoles.
  SLOT 0 $8000                  ; Defines Slot 0's starting address.
  SLOT 1 $0 $80					; tcc direct page vars
  SLOT 2 $2000 $6000			; half of the page
  SLOT 3 $0 $4000				; quarter of the page
  SLOT 4 $80 $1f80				; assembly code direct page vars
.ENDME  

.ROMBANKSIZE $8000              ; Every ROM bank is 32 KBytes in size
.ROMBANKS 16                    ; Tell WLA how many ROM banks we want

.SNESHEADER
  ID "SNES"                     ; 1-4 letter string, just leave it as "SNES"

  NAME "HINDSTRIKE           "  ; Program Title - can't be over 21 bytes,
  ;    "123456789012345678901"  ; use spaces for unused bytes of the name.

  FASTROM;SLOWROM
  LOROM

  CARTRIDGETYPE $05
	;$00  ROM only
	;$01  ROM and RAM
	;$02  ROM and Save RAM
	;$03  ROM and DSP1 chip
	;$04  ROM, RAM and DSP1 chip
	;$05  ROM, Save RAM and DSP1 chip
	;$13  ROM and Super FX chip
	;$13  SuperFX with no battery
	;$14  SuperFX with no battery
	;$15  SuperFX with save-RAM
	;$1a  SuperFX with save-RAM
	;$34  SA-1
	;$35  SA-1 

  ROMSIZE $09
	;$08 - 2 Megabits (8x32K banks)
	;$09 - 4 Megabits
	;$0A - 8 Megabits
	;$0B - 16 Megabits
	;$0C - 32 Megabits
	
  SRAMSIZE $00
	;$00 - No SRAM
	;$01 - 16 kilobits
	;$02 - 32 kilobits
	;$03 - 64 kilobits

  COUNTRY $01
	;$00      NTSC Japan
	;$01      NTSC US
	;$02..$0c PAL
	;$0d      NTSC
	;$0e..$ff invalid 

  LICENSEECODE $00              ; Just use $00
  VERSION $00                   ; $00 = 1.00, $01 = 1.01, etc.
.ENDSNES

.SNESNATIVEVECTOR               ; Define Native Mode interrupt vector table
  COP EmptyHandler
  BRK EmptyHandler
  ABORT EmptyHandler
  NMI VBlank
  IRQ EmptyHandler
.ENDNATIVEVECTOR

.SNESEMUVECTOR                  ; Define Emulation Mode interrupt vector table
  COP EmptyHandler
  ABORT EmptyHandler
  NMI EmptyHandler
  RESET tcc__start              ; where execution starts
  IRQBRK EmptyHandler
.ENDEMUVECTOR
