.MEMORYMAP
  SLOTSIZE $%bank_size
  DEFAULTSLOT 0
  SLOT 0 $0000
.ENDME  

.ROMBANKSIZE $%bank_size		; Every ROM bank is 32 KBytes in size
.ROMBANKS %rom_banks			; Tell WLA how many ROM banks we want

.SNESHEADER
  ID "SNES"						; 1-4 letter string, just leave it as "SNES"

  NAME "%title"  ; Program Title - can't be over 21 bytes,
  ;    "123456789012345678901"  ; use spaces for unused bytes of the name.
  %rom_speed
  %rom_map

  CARTRIDGETYPE $%cart_type
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

  ROMSIZE $%rom_size
	;$08 - 2 Megabits (8x32K banks)
	;$09 - 4 Megabits
	;$0A - 8 Megabits
	;$0B - 16 Megabits
	;$0C - 32 Megabits
	
  SRAMSIZE $%sram_size
	;$00 - No SRAM
	;$01 - 16 kilobits
	;$02 - 32 kilobits
	;$03 - 64 kilobits

  COUNTRY $%country
	;$00      NTSC Japan
	;$01      NTSC US
	;$02..$0c PAL
	;$0d      NTSC
	;$0e..$ff invalid 

  LICENSEECODE $%license_code              ; Just use $00
  VERSION $%version                   ; $00 = 1.00, $01 = 1.01, etc.
.ENDSNES

.SNESNATIVEVECTOR               ; Define Native Mode interrupt vector table
  COP %nvec_cop
  BRK %nvec_brk
  ABORT %nvec_abort
  NMI %nvec_nmi
  IRQ %nvec_irq
.ENDNATIVEVECTOR

.SNESEMUVECTOR                  ; Define Emulation Mode interrupt vector table
  COP %evec_cop
  ABORT %evec_abort
  NMI %evec_nmi
  RESET %evec_reset              ; where execution starts
  IRQBRK %evec_irq
.ENDEMUVECTOR
