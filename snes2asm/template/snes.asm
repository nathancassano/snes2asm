;SNES register definitions

;PPU regs
.define INIDSP $2100					;Screen Display
	.define INIDSP_FORCE_BLANK			1 << 7
	.define INIDSP_BRIGHTNESS			$f << 0

.define OBJSEL $2101					;Object Size and Chr Address
	.define OBJSEL_SPRITES_8X8_16X16	0 << 5
	.define OBJSEL_SPRITES_8X8_32X32	1 << 5
	.define OBJSEL_SPRITES_8X8_64X64	2 << 5
	.define OBJSEL_SPRITES_16X16_32X32	3 << 5
	.define OBJSEL_SPRITES_16X16_64X64	4 << 5
	.define OBJSEL_SPRITES_32X32_64X64	5 << 5
	.define OBJSEL_SPRITES_16X32_32X64	6 << 5
	.define OBJSEL_SPRITES_16X32_32X32	7 << 5
	.define OBJSEL_BASE_0000			0
	.define OBJSEL_BASE_4000			1
	.define OBJSEL_BASE_8000			2
	.define OBJSEL_BASE_C000			3
	.define OBJSEL_NAME_PLUS_1000   	0 << 3
	.define OBJSEL_NAME_PLUS_2000		1 << 3
	.define OBJSEL_NAME_PLUS_3000		2 << 3
	.define OBJSEL_NAME_PLUS_4000		3 << 3

.define OAMADDL $2102					;OAM Address
.define OAMADDH $2103
	.define OAMADDH_PRIORITY_ACTIVATE	1 << 7

.define OAMDATA $2104					;Data for OAM write

.define BGMODE $2105					;BG Mode and Character Size
	.define BGMODE_CHARSIZE_LAYER_4		1 << 7
	.define BGMODE_CHARSIZE_LAYER_3		1 << 6
	.define BGMODE_CHARSIZE_LAYER_2		1 << 5
	.define BGMODE_CHARSIZE_LAYER_1		1 << 4
	.define BGMODE_PRIORITY_LAYER_3		1 << 3
	.define BGMODE_MODE_7				7
	.define BGMODE_MODE_6				6
	.define BGMODE_MODE_5				5
	.define BGMODE_MODE_4				4
	.define BGMODE_MODE_3				3
	.define BGMODE_MODE_2				2
	.define BGMODE_MODE_1				1
	.define BGMODE_MODE_0				0

.define MOSAIC $2106					;Screen Pixelation
	.define MOSAIC_LAYER_4				1 << 3
	.define MOSAIC_LAYER_3				1 << 2
	.define MOSAIC_LAYER_2				1 << 1
	.define MOSAIC_LAYER_1				1 << 0

.define BG1SC $2107						;BG Tilemap Address and Size
.define BG2SC $2108
.define BG3SC $2109
.define BG4SC $210a
 	.define BGSC_Y_MIRROR				1 << 1
	.define BGSC_X_MIRROR				1 << 0

.define BG12NBA $210b					;BG Chr(Tiles) Address
	.define BG1NBA_0000					0 << 0
	.define BG1NBA_2000					1 << 0
	.define BG1NBA_4000					2 << 0
	.define BG1NBA_6000					3 << 0
	.define BG1NBA_8000					4 << 0
	.define BG1NBA_A000					5 << 0
	.define BG1NBA_C000					6 << 0
	.define BG1NBA_E000					7 << 0

	.define BG2NBA_0000					0 << 4
	.define BG2NBA_2000					1 << 4
	.define BG2NBA_4000					2 << 4
	.define BG2NBA_6000					3 << 4
	.define BG2NBA_8000					4 << 4
	.define BG2NBA_A000					5 << 4
	.define BG2NBA_C000					6 << 4
	.define BG2NBA_E000					7 << 4

.define BG34NBA $210c
	.define BG3NBA_0000					0 << 0
	.define BG3NBA_2000					1 << 0
	.define BG3NBA_4000					2 << 0
	.define BG3NBA_6000					3 << 0
	.define BG3NBA_8000					4 << 0
	.define BG3NBA_A000					5 << 0
	.define BG3NBA_C000					6 << 0
	.define BG3NBA_E000					7 << 0

	.define BG4NBA_0000					0 << 4
	.define BG4NBA_2000					1 << 4
	.define BG4NBA_4000					2 << 4
	.define BG4NBA_6000					3 << 4
	.define BG4NBA_8000					4 << 4
	.define BG4NBA_A000					5 << 4
	.define BG4NBA_C000					6 << 4
	.define BG4NBA_E000					7 << 4

.define BG1HOFS $210d					;BG x-Scroll
.define M7HOFS $210d
.define BG1VOFS $210e					;BG y-Scroll
.define M7VOFS $210e

.define BG2HOFS $210f
.define BG2VOFS $2110

.define BG3HOFS $2111
.define BG3VOFS $2112

.define BG4HOFS $2113
.define BG4VOFS $2114

.define VMAIN $2115						;Video Port Control
	.define VMAIN_INCREMENT_MODE		1 << 7
	.define VMAIN_INCREMENT_1			0 << 0
	.define VMAIN_INCREMENT_32			1 << 0
	.define VMAIN_INCREMENT_128			2 << 0

.define VMADDL $2116					;VRAM Address
.define VMADDH $2117

.define VMDATAL $2118					;VRAM Data
.define VMDATAH $2119

.define M7SEL $211a						;Mode 7 Settings
	.define M7SEL_PLAYFIELD_SIZE		1 << 7
	.define M7SEL_EMPTY_FILL			1 << 6
	.define M7SEL_Y_MIRROR				1 << 1
	.define M7SEL_X_MIRROR				1 << 0

.define M7A $211b						;Mode 7 Matrix
.define M7B $211c
.define M7C $211d
.define M7D $211e
.define M7X $211f						;Mode 7 Center
.define M7Y $2120

.define CGADD $2121						;CGRAM Address
.define CGDATA $2122					;CGRAM Data

.define W12SEL $2123					;Window Mask Settings
	.define W12SEL_BG2_W2_ENABLE		1 << 7
	.define W12SEL_BG2_W2_INVERT		1 << 6
	.define W12SEL_BG2_W1_ENABLE		1 << 5
	.define W12SEL_BG2_W1_INVERT		1 << 4
	.define W12SEL_BG1_W2_ENABLE		1 << 3
	.define W12SEL_BG1_W2_INVERT		1 << 2
	.define W12SEL_BG1_W1_ENABLE		1 << 1
	.define W12SEL_BG1_W1_INVERT		1 << 0

.define W34SEL $2124
	.define W34SEL_BG4_W2_ENABLE		1 << 7
	.define W34SEL_BG4_W2_INVERT		1 << 6
	.define W34SEL_BG4_W1_ENABLE		1 << 5
	.define W34SEL_BG4_W1_INVERT		1 << 4
	.define W34SEL_BG3_W2_ENABLE		1 << 3
	.define W34SEL_BG3_W2_INVERT		1 << 2
	.define W34SEL_BG3_W1_ENABLE		1 << 1
	.define W34SEL_BG3_W1_INVERT		1 << 0

.define WOBJSEL $2125
	.define WOBJSEL_COL_W2_ENABLE		1 << 7
	.define WOBJSEL_COL_W2_INVERT		1 << 6
	.define WOBJSEL_COL_W1_ENABLE		1 << 5
	.define WOBJSEL_COL_W1_INVERT		1 << 4
	.define WOBJSEL_OBJ_W2_ENABLE		1 << 3
	.define WOBJSEL_OBJ_W2_INVERT		1 << 2
	.define WOBJSEL_OBJ_W1_ENABLE		1 << 1
	.define WOBJSEL_OBJ_W1_INVERT		1 << 0

.define W1L $2126	;WH0				;Window Position
.define W1R $2127	;WH1
.define W2L $2128	;WH2
.define W2R $2129	;WH3

.define WBGLOG $212a					;Window mask logic
	.define WBGLOG_BG4_OR				0 << 6
	.define WBGLOG_BG4_AND				1 << 6
	.define WBGLOG_BG4_XOR				2 << 6
	.define WBGLOG_BG4_XNOR				3 << 6

	.define WBGLOG_BG3_OR				0 << 4
	.define WBGLOG_BG3_AND				1 << 4
	.define WBGLOG_BG3_XOR				2 << 4
	.define WBGLOG_BG3_XNOR				3 << 4

	.define WBGLOG_BG2_OR				0 << 2
	.define WBGLOG_BG2_AND				1 << 2
	.define WBGLOG_BG2_XOR				2 << 2
	.define WBGLOG_BG2_XNOR				3 << 2

	.define WBGLOG_BG1_OR				0 << 0
	.define WBGLOG_BG1_AND				1 << 0
	.define WBGLOG_BG1_XOR				2 << 0
	.define WBGLOG_BG1_XNOR				3 << 0

.define WOBJLOG $212b
	.define WOBJLOG_COL_OR				0 << 2
	.define WOBJLOG_COL_AND				1 << 2
	.define WOBJLOG_COL_XOR				2 << 2
	.define WOBJLOG_COL_XNOR			3 << 2

	.define WOBJLOG_OBJ_OR				0 << 0
	.define WOBJLOG_OBJ_AND				1 << 0
	.define WOBJLOG_OBJ_XOR				2 << 0
	.define WOBJLOG_OBJ_XNOR			3 << 0

.define TMAIN $212c						;Mainscreen Designation
.define TSUB $212d						;Subscreen Designation
.define TMW $212e						;Mainscreen Window Mask Designation
.define TSW $212f						;Subscreen Mask Designation
 	.define T_OBJ_ENABLE				1 << 4
 	.define T_BG4_ENABLE				1 << 3
 	.define T_BG3_ENABLE				1 << 2
 	.define T_BG2_ENABLE				1 << 1
 	.define T_BG1_ENABLE				1 << 0

.define CGWSEL $2130					;Color Addition Select
 	.define CGWSEL_CLIP_COL_NEVER		0 << 6
 	.define CGWSEL_CLIP_COL_OUTSIDE		1 << 6
 	.define CGWSEL_CLIP_COL_INSIDE		2 << 6
 	.define CGWSEL_CLIP_COL_ALWAYS		3 << 6

 	.define CGWSEL_NO_COL_MATH_NEVER	0 << 4
 	.define CGWSEL_NO_COL_MATH_OUTSIDE	1 << 4
 	.define CGWSEL_NO_COL_MATH_INSIDE	2 << 4
 	.define CGWSEL_NO_COL_MATH_ALWAYS	3 << 4

	.define CGWSEL_ADD_SUBSCREEN		1 << 1
	.define CGWSEL_DIRECT_COLOR_MODE	1 << 0

.define CGADSUB $2131					;Color math designation
 	.define CGADSUB_ADDSUB_COL			1 << 7
 	.define CGADSUB_HALF_COL			1 << 6
	.define CGADSUB_BAC_ENABLE			1 << 5
	.define CGADSUB_OBJ_ENABLE			1 << 4
	.define CGADSUB_BG4_ENABLE			1 << 3
	.define CGADSUB_BG3_ENABLE			1 << 2
	.define CGADSUB_BG2_ENABLE			1 << 1
	.define CGADSUB_BG1_ENABLE			1 << 0

.define COLDATA $2132					;Fixed Color Data
 	.define COLDATA_BLUE				1 << 7
 	.define COLDATA_GREEN				1 << 6
 	.define COLDATA_RED					1 << 5
	.define COLDATA_INTENSITY			$1f << 0

.define SETINI $2133					;Screen Mode/Video Select
 	.define SETINI_EXT_SYNC				1 << 7
 	.define SETINI_MODE7_EXTBG			1 << 6
 	.define SETINI_PSEUDO_HIRES			1 << 3
 	.define SETINI_OVERSCAN				1 << 2
 	.define SETINI_OBJ_INTERLACE		1 << 1
 	.define SETINI_SCREEN_INTERLACE		1 << 0

.define MPYL $2134						;Multiplication Result
.define MPYM $2135
.define MPYH $2136

.define SLHV $2137						;Software Latch for H/V Counter

.define OAMDATAREAD $2138				;Data for OAM read

.define VMDATALREAD $2139				;VRAM Data Read
.define VMDATAHREAD $213a

.define CGDATAREAD $213b				;CGRAM Data read

.define OPHCT $213c						;Scanline Location
  	.define OPH_MASK					$01ff
.define OPVCT $213d
  	.define OPV_MASK					$01ff
  	.define OPV_NMI						225

.define STAT77 $213e					;5C77 PPU-1 Status Flag and Version
 	.define STAT77_TIME_OVER			1 << 7
 	.define STAT77_RANGE_OVER			1 << 6
 	.define STAT77_PPU_SLAVE_MASTER		1 << 5

.define STAT78 $213f					;5C78 PPU-2 Status Flag and Version
 	.define STAT78_INTERLACE_FIELD		1 << 7
 	.define STAT78_EXT_LATCH			1 << 6
 	.define STAT78_NTSC_PAL				1 << 4

.define APUIO0 $2140					;APU I/O Ports
.define APUIO1 $2141
.define APUIO2 $2142
.define APUIO3 $2143

.define WMDATA $2180					;WRAM Data Port
.define WMADDL $2181					;WRAM Address
.define WMADDM $2182
.define WMADDH $2183


;cpu regs:
.define JOYSER0 $4016					;Joypad Port 1
  .define JOYSER0_DATA2					1 << 1
  .define JOYSER0_DATA1					1 << 0
  .define JOYSER0_LATCH					1 << 0

.define JOYSER1 $4017					;Joypad Port 2
  .define JOYSER1_DATA2					1 << 1
  .define JOYSER1_DATA1					1 << 0

.define NMITIMEN $4200					;Interrupt Enable Flags
  .define NMITIMEN_NMI_ENABLE			1 << 7
  .define NMITIMEN_Y_IRQ_ENABLE			1 << 5
  .define NMITIMEN_X_IRQ_ENABLE			1 << 4
  .define NMITIMEN_AUTO_JOY_READ		1 << 0


.define WRIO $4201						;I/O port output/write
  .define WRIO_JOY2_IOBIT_LATCH			1 << 7
  .define WRIO_JOY1_IOBIT				1 << 6

.define WRMPYA $4202					;Multiplicand
.define WRMPYB $4203
.define WRDIVL $4204					;Dividend
.define WRDIVH $4205
.define WRDIVB $4206					;Divisor

.define HTIMEL $4207					;H/X Timer
.define HTIMEH $4208
.define VTIMEL $4209					;V/Y Timer
.define VTIMEH $420a
  .define TIMER_RANGE					$1f

.define MDMAEN $420b					;DMA Enable
.define HDMAEN $420c					;HDMA Enable
  .define DMA_CHANNEL7_ENABLE			1 << 7
  .define DMA_CHANNEL6_ENABLE			1 << 6
  .define DMA_CHANNEL5_ENABLE			1 << 5
  .define DMA_CHANNEL4_ENABLE			1 << 4
  .define DMA_CHANNEL3_ENABLE			1 << 3
  .define DMA_CHANNEL2_ENABLE			1 << 2
  .define DMA_CHANNEL1_ENABLE			1 << 1
  .define DMA_CHANNEL0_ENABLE			1 << 0

.define MEMSEL $420d					;ROM Access Speed
  .define MEMSEL_FASTROM_ENABLE			1 << 0

.define RDNMI $4210						;NMI Flag and 5A22 Version
  .define RDNMI_NMI_FLAG				1 << 7

.define TIMEUP $4211					;IRQ Flag
  .define TIMEUP_IRQ_FLAG				1 << 7

.define HVBJOY $4212					;PPU Status
  .define HVBJOY_VBLANK_FLAG			1 << 7
  .define HVBJOY_HBLANK_FLAG			1 << 6
  .define HVBJOY_AUTO_JOY_STATUS		1 << 0

.define RDIO $4213						;I/O port input/read
  .define RDIO_JOY2_IOBIT_LATCH			1 << 7
  .define RDIO_JOY1_IOBIT				1 << 6

.define RDDIVL $4214					;Quotient of Divide Result
.define RDDIVH $4215
.define RDMPYL $4216					;Multiplication Product or Divide Remainder
.define RDMPYH $4217

.define JOY1L $4218						;Joyport1 Data1
.define JOY1H $4219
.define JOY2L $421a						;Joyport2 Data1
.define JOY2H $421b
.define JOY3L $421c						;Joyport1 Data2
.define JOY3H $421d
.define JOY4L $421e						;Joyport2 Data2
.define JOY4H $421f
  .define JOY_BUTTON_B					1 << 15
  .define JOY_BUTTON_Y					1 << 14
  .define JOY_BUTTON_SELECT				1 << 13
  .define JOY_BUTTON_START				1 << 12
  .define JOY_DIR_UP					1 << 11
  .define JOY_DIR_DOWN					1 << 10
  .define JOY_DIR_LEFT					1 << 9
  .define JOY_DIR_RIGHT					1 << 8
  .define JOY_BUTTON_A					1 << 7
  .define JOY_BUTTON_X					1 << 6
  .define JOY_BUTTON_L					1 << 5
  .define JOY_BUTTON_R					1 << 4

  .define JOY_BUTTON_SIGNATURE			%1111

.define DMAP0 $4300						;DMA Control
  .define DMAP_TRANSFER_DIRECTION		1 << 7
  .define DMAP_HDMA_INDIRECT_MODE		1 << 6
  .define DMAP_ADRESS_INCREMENT			1 << 4
  .define DMAP_FIXED_TRANSFER			1 << 3
  .define DMAP_1_REG_WRITE_ONCE			0 << 0
  .define DMAP_2_REG_WRITE_ONCE			1 << 0
  .define DMAP_1_REG_WRITE_TWICE		2 << 0
  .define DMAP_2_REG_WRITE_TWICE_EACH	3 << 0
  .define DMAP_4_REG_WRITE_ONCE			4 << 0
  .define DMAP_2_REG_WRITE_TWICE_ALT	5 << 0

.define DMADEST0 $4301					;DMA Destination Register

.define DMASRC0L $4302					;DMA Source Adress
.define DMASRC0H $4303
.define DMASRC0B $4304

.define DMALEN0L $4305					;DMA Size/HDMA Indirect Adress
.define DMALEN0H $4306
.define DMALEN0B $4307

.define HDMATBL0L $4308					;HDMA Table Address
.define HDMATBL0H $4309

.define HDMACNT0 $430a					;HDMA Line Counter
  .define HDMACNT_REPEAT				1 << 7
  .define HDMACNT_RANGE					$7f

.define DMAP1		$4310
.define DMADEST1	$4311
.define DMASRC1L	$4312
.define DMASRC1H	$4313
.define DMASRC1B	$4314
.define DMALEN1L	$4315
.define DMALEN1H	$4316
.define DMALEN1B	$4317
.define HDMATBL1L	$4318
.define HDMATBL1H	$4319
.define HDMACNT1	$431a

.define DMAP2		$4320
.define DMADEST2	$4321
.define DMASRC2L	$4322
.define DMASRC2H	$4323
.define DMASRC2B	$4324
.define DMALEN2L	$4325
.define DMALEN2H	$4326
.define DMALEN2B	$4327
.define HDMATBL2L	$4328
.define HDMATBL2H	$4329
.define HDMACNT2	$432a

.define DMAP3		$4330
.define DMADEST3	$4331
.define DMASRC3L	$4332
.define DMASRC3H	$4333
.define DMASRC3B	$4334
.define DMALEN3L	$4335
.define DMALEN3H	$4336
.define DMALEN3B	$4337
.define HDMATBL3L	$4338
.define HDMATBL3H	$4339
.define HDMACNT3	$433a

.define DMAP4		$4340
.define DMADEST4	$4341
.define DMASRC4L	$4342
.define DMASRC4H	$4343
.define DMASRC4B	$4344
.define DMALEN4L	$4345
.define DMALEN4H	$4346
.define DMALEN4B	$4347
.define HDMATBL4L	$4348
.define HDMATBL4H	$4349
.define HDMACNT4	$434a

.define DMAP5		$4350
.define DMADEST5	$4351
.define DMASRC5L	$4352
.define DMASRC5H	$4353
.define DMASRC5B	$4354
.define DMALEN5L	$4355
.define DMALEN5H	$4356
.define DMALEN5B	$4357
.define HDMATBL5L	$4358
.define HDMATBL5H	$4359
.define HDMACNT5	$435a

.define DMAP6		$4360
.define DMADEST6	$4361
.define DMASRC6L	$4362
.define DMASRC6H	$4363
.define DMASRC6B	$4364
.define DMALEN6L	$4365
.define DMALEN6H	$4366
.define DMALEN6B	$4367
.define HDMATBL6L	$4368
.define HDMATBL6H	$4369
.define HDMACNT6	$436a

.define DMAP7		$4370
.define DMADEST7	$4371
.define DMASRC7L	$4372
.define DMASRC7H	$4373
.define DMASRC7B	$4374
.define DMALEN7L	$4375
.define DMALEN7H	$4376
.define DMALEN7B	$4377
.define HDMATBL7L	$4378
.define HDMATBL7H	$4379
.define HDMACNT7	$437a

;tilemap format in vram:
.define BG.FORMAT.TILE $3ff
.define BG.FORMAT.PALETTE $1C00
.define BG.FORMAT.PALETTE.1 $400
.define BG.FORMAT.PALETTE.2 $800
.define BG.FORMAT.PRIORITY $2000
.define BG.FORMAT.HFLIP $4000
.define BG.FORMAT.VFLIP $8000

;sprite format in oamram:
.define OAM.FORMAT.TILE $1ff
.define OAM.FORMAT.PALETTE $0E00
.define OAM.FORMAT.PRIORITY $3000
.define OAM.FORMAT.HFLIP $4000
.define OAM.FORMAT.VFLIP $8000
