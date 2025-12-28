;SPC700 I/O Register Definitions
;Sony SPC700 Audio Processor Registers

;==============================================================================
; Communication Ports (CPU <-> SPC700)
;==============================================================================
.define APUIO0 $F4					;APU I/O Port 0 (CPU: $2140)
.define APUIO1 $F5					;APU I/O Port 1 (CPU: $2141)
.define APUIO2 $F6					;APU I/O Port 2 (CPU: $2142)
.define APUIO3 $F7					;APU I/O Port 3 (CPU: $2143)

;==============================================================================
; Control and Test Registers
;==============================================================================
.define TEST $F0					;Test Register (typically unused)

.define CONTROL $F1					;Control Register
	.define CONTROL_TIMER0_ENABLE		1 << 0
	.define CONTROL_TIMER1_ENABLE		1 << 1
	.define CONTROL_TIMER2_ENABLE		1 << 2
	.define CONTROL_RESET_PORTS_4_5		1 << 4
	.define CONTROL_RESET_PORTS_6_7		1 << 5
	.define CONTROL_IPL_ROM_ENABLE		1 << 7

;==============================================================================
; DSP Interface Registers
;==============================================================================
.define DSPADDR $F2					;DSP Register Address
.define DSPDATA $F3					;DSP Register Data

;==============================================================================
; Timer Registers
;==============================================================================
.define T0DIV $FA					;Timer 0 Divider (8000 Hz / n)
.define T1DIV $FB					;Timer 1 Divider (8000 Hz / n)
.define T2DIV $FC					;Timer 2 Divider (64000 Hz / n)

.define T0OUT $FD					;Timer 0 Counter Output (read-only)
.define T1OUT $FE					;Timer 1 Counter Output (read-only)
.define T2OUT $FF					;Timer 2 Counter Output (read-only)

;==============================================================================
; Timer Common Values
;==============================================================================
; Timer frequency = base_freq / divider
; Timer 0/1: 8000 Hz base (125 us per tick)
; Timer 2: 64000 Hz base (15.625 us per tick)

	.define TIMER0_1MS			8		;8000 Hz / 8 = 1000 Hz (1ms)
	.define TIMER0_2MS			16		;8000 Hz / 16 = 500 Hz (2ms)
	.define TIMER0_4MS			32		;8000 Hz / 32 = 250 Hz (4ms)
	.define TIMER0_8MS			64		;8000 Hz / 64 = 125 Hz (8ms)
	.define TIMER0_16MS			128		;8000 Hz / 128 = 62.5 Hz (16ms)
	.define TIMER0_32MS			256		;8000 Hz / 256 = 31.25 Hz (32ms)

	.define TIMER1_1MS			8		;8000 Hz / 8 = 1000 Hz (1ms)
	.define TIMER1_2MS			16		;8000 Hz / 16 = 500 Hz (2ms)
	.define TIMER1_4MS			32		;8000 Hz / 32 = 250 Hz (4ms)
	.define TIMER1_8MS			64		;8000 Hz / 64 = 125 Hz (8ms)
	.define TIMER1_16MS			128		;8000 Hz / 128 = 62.5 Hz (16ms)
	.define TIMER1_32MS			256		;8000 Hz / 256 = 31.25 Hz (32ms)

	.define TIMER2_1MS			64		;64000 Hz / 64 = 1000 Hz (1ms)
	.define TIMER2_500US		32		;64000 Hz / 32 = 2000 Hz (0.5ms)
	.define TIMER2_250US		16		;64000 Hz / 16 = 4000 Hz (0.25ms)

;==============================================================================
; DSP Register Addresses (accessed via $F2/$F3)
;==============================================================================
; Voice 0 Registers
.define DSP_V0_VOLL		$00				;Voice 0 Volume Left
.define DSP_V0_VOLR		$01				;Voice 0 Volume Right
.define DSP_V0_PITCHL	$02				;Voice 0 Pitch Low
.define DSP_V0_PITCHH	$03				;Voice 0 Pitch High
.define DSP_V0_SRCN		$04				;Voice 0 Source Number
.define DSP_V0_ADSR1	$05				;Voice 0 ADSR1
.define DSP_V0_ADSR2	$06				;Voice 0 ADSR2
.define DSP_V0_GAIN		$07				;Voice 0 Gain
.define DSP_V0_ENVX		$08				;Voice 0 Envelope (read-only)
.define DSP_V0_OUTX		$09				;Voice 0 Output (read-only)

; Voice 1 Registers
.define DSP_V1_VOLL		$10
.define DSP_V1_VOLR		$11
.define DSP_V1_PITCHL	$12
.define DSP_V1_PITCHH	$13
.define DSP_V1_SRCN		$14
.define DSP_V1_ADSR1	$15
.define DSP_V1_ADSR2	$16
.define DSP_V1_GAIN		$17
.define DSP_V1_ENVX		$18
.define DSP_V1_OUTX		$19

; Voice 2 Registers
.define DSP_V2_VOLL		$20
.define DSP_V2_VOLR		$21
.define DSP_V2_PITCHL	$22
.define DSP_V2_PITCHH	$23
.define DSP_V2_SRCN		$24
.define DSP_V2_ADSR1	$25
.define DSP_V2_ADSR2	$26
.define DSP_V2_GAIN		$27
.define DSP_V2_ENVX		$28
.define DSP_V2_OUTX		$29

; Voice 3 Registers
.define DSP_V3_VOLL		$30
.define DSP_V3_VOLR		$31
.define DSP_V3_PITCHL	$32
.define DSP_V3_PITCHH	$33
.define DSP_V3_SRCN		$34
.define DSP_V3_ADSR1	$35
.define DSP_V3_ADSR2	$36
.define DSP_V3_GAIN		$37
.define DSP_V3_ENVX		$38
.define DSP_V3_OUTX		$39

; Voice 4 Registers
.define DSP_V4_VOLL		$40
.define DSP_V4_VOLR		$41
.define DSP_V4_PITCHL	$42
.define DSP_V4_PITCHH	$43
.define DSP_V4_SRCN		$44
.define DSP_V4_ADSR1	$45
.define DSP_V4_ADSR2	$46
.define DSP_V4_GAIN		$47
.define DSP_V4_ENVX		$48
.define DSP_V4_OUTX		$49

; Voice 5 Registers
.define DSP_V5_VOLL		$50
.define DSP_V5_VOLR		$51
.define DSP_V5_PITCHL	$52
.define DSP_V5_PITCHH	$53
.define DSP_V5_SRCN		$54
.define DSP_V5_ADSR1	$55
.define DSP_V5_ADSR2	$56
.define DSP_V5_GAIN		$57
.define DSP_V5_ENVX		$58
.define DSP_V5_OUTX		$59

; Voice 6 Registers
.define DSP_V6_VOLL		$60
.define DSP_V6_VOLR		$61
.define DSP_V6_PITCHL	$62
.define DSP_V6_PITCHH	$63
.define DSP_V6_SRCN		$64
.define DSP_V6_ADSR1	$65
.define DSP_V6_ADSR2	$66
.define DSP_V6_GAIN		$67
.define DSP_V6_ENVX		$68
.define DSP_V6_OUTX		$69

; Voice 7 Registers
.define DSP_V7_VOLL		$70
.define DSP_V7_VOLR		$71
.define DSP_V7_PITCHL	$72
.define DSP_V7_PITCHH	$73
.define DSP_V7_SRCN		$74
.define DSP_V7_ADSR1	$75
.define DSP_V7_ADSR2	$76
.define DSP_V7_GAIN		$77
.define DSP_V7_ENVX		$78
.define DSP_V7_OUTX		$79

; Global DSP Registers
.define DSP_MVOLL		$0C				;Main Volume Left
.define DSP_MVOLR		$1C				;Main Volume Right
.define DSP_EVOLL		$2C				;Echo Volume Left
.define DSP_EVOLR		$3C				;Echo Volume Right
.define DSP_KON			$4C				;Key On
.define DSP_KOFF		$5C				;Key Off
.define DSP_FLG			$6C				;DSP Flags
.define DSP_ENDX		$7C				;Voice End (read-only)

.define DSP_EFB			$0D				;Echo Feedback
.define DSP_PMOD		$2D				;Pitch Modulation Enable
.define DSP_NON			$3D				;Noise Enable
.define DSP_EON			$4D				;Echo Enable
.define DSP_DIR			$5D				;Sample Table Directory
.define DSP_ESA			$6D				;Echo Buffer Start Address
.define DSP_EDL			$7D				;Echo Delay Length

; Echo FIR Filter Coefficients
.define DSP_FIR0		$0F
.define DSP_FIR1		$1F
.define DSP_FIR2		$2F
.define DSP_FIR3		$3F
.define DSP_FIR4		$4F
.define DSP_FIR5		$5F
.define DSP_FIR6		$6F
.define DSP_FIR7		$7F

;==============================================================================
; DSP Flag Register ($6C) Bit Definitions
;==============================================================================
	.define DSP_FLG_SOFT_RESET			1 << 7
	.define DSP_FLG_MUTE				1 << 6
	.define DSP_FLG_ECHO_DISABLE		1 << 5
	.define DSP_FLG_NOISE_FREQ_32KHZ	0 << 0
	.define DSP_FLG_NOISE_FREQ_16KHZ	1 << 0
	.define DSP_FLG_NOISE_FREQ_8KHZ		2 << 0
	.define DSP_FLG_NOISE_FREQ_4KHZ		3 << 0
	.define DSP_FLG_NOISE_FREQ_2KHZ		4 << 0
	.define DSP_FLG_NOISE_FREQ_1KHZ		5 << 0
	.define DSP_FLG_NOISE_FREQ_500HZ	6 << 0
	.define DSP_FLG_NOISE_FREQ_250HZ	7 << 0
	.define DSP_FLG_NOISE_FREQ_125HZ	8 << 0
	.define DSP_FLG_NOISE_FREQ_62HZ		9 << 0
	.define DSP_FLG_NOISE_FREQ_31HZ		10 << 0
	.define DSP_FLG_NOISE_FREQ_15HZ		11 << 0
	.define DSP_FLG_NOISE_FREQ_7HZ		12 << 0
	.define DSP_FLG_NOISE_FREQ_4HZ		13 << 0
	.define DSP_FLG_NOISE_FREQ_2HZ		14 << 0
	.define DSP_FLG_NOISE_FREQ_1HZ		15 << 0
	.define DSP_FLG_NOISE_FREQ_0_5HZ	16 << 0
	.define DSP_FLG_NOISE_FREQ_0_25HZ	17 << 0
	.define DSP_FLG_NOISE_FREQ_0_125HZ	18 << 0
	.define DSP_FLG_NOISE_FREQ_0_0625HZ	19 << 0
	.define DSP_FLG_NOISE_FREQ_0_03125HZ 20 << 0
	.define DSP_FLG_NOISE_FREQ_0_015625HZ 21 << 0
	.define DSP_FLG_NOISE_FREQ_0_0078125HZ 22 << 0
	.define DSP_FLG_NOISE_FREQ_0_00390625HZ 23 << 0
	.define DSP_FLG_NOISE_FREQ_0_001953125HZ 24 << 0
	.define DSP_FLG_NOISE_FREQ_0_0009765625HZ 25 << 0
	.define DSP_FLG_NOISE_FREQ_0_00048828125HZ 26 << 0
	.define DSP_FLG_NOISE_FREQ_0_000244140625HZ 27 << 0
	.define DSP_FLG_NOISE_FREQ_0_0001220703125HZ 28 << 0
	.define DSP_FLG_NOISE_FREQ_0_00006103515625HZ 29 << 0
	.define DSP_FLG_NOISE_FREQ_0_000030517578125HZ 30 << 0
	.define DSP_FLG_NOISE_FREQ_0_0000152587890625HZ 31 << 0

;==============================================================================
; ADSR1 Register Bit Definitions
;==============================================================================
	.define DSP_ADSR1_ENABLE			1 << 7
	.define DSP_ADSR1_DECAY_MASK		$70
	.define DSP_ADSR1_ATTACK_MASK		$0F

;==============================================================================
; ADSR2 Register Bit Definitions
;==============================================================================
	.define DSP_ADSR2_SUSTAIN_LEVEL_MASK	$E0
	.define DSP_ADSR2_SUSTAIN_RATE_MASK		$1F

;==============================================================================
; GAIN Register Bit Definitions
;==============================================================================
	.define DSP_GAIN_DIRECT				0 << 7		;Direct gain mode
	.define DSP_GAIN_ENVELOPE			1 << 7		;Envelope mode
	.define DSP_GAIN_MODE_LINEAR_DEC	0 << 5		;Linear decrease
	.define DSP_GAIN_MODE_EXP_DEC		1 << 5		;Exponential decrease
	.define DSP_GAIN_MODE_LINEAR_INC	2 << 5		;Linear increase
	.define DSP_GAIN_MODE_BENT_INC		3 << 5		;Bent line increase
	.define DSP_GAIN_RATE_MASK			$1F

;==============================================================================
; Common Volume Values
;==============================================================================
	.define VOL_FULL		$7F				;Maximum volume
	.define VOL_HALF		$40				;50% volume
	.define VOL_QUARTER		$20				;25% volume
	.define VOL_MUTE		$00				;Mute/silence

;==============================================================================
; Common Pitch Values (middle C = $1000)
;==============================================================================
	.define PITCH_C4		$1000			;Middle C (261.63 Hz)
	.define PITCH_NORMAL	$1000			;Normal playback rate
	.define PITCH_DOUBLE	$2000			;Double speed (octave up)
	.define PITCH_HALF		$0800			;Half speed (octave down)

;==============================================================================
; Voice Bit Masks (for KON, KOFF, PMON, NON, EON, ENDX)
;==============================================================================
	.define VOICE0_BIT		1 << 0
	.define VOICE1_BIT		1 << 1
	.define VOICE2_BIT		1 << 2
	.define VOICE3_BIT		1 << 3
	.define VOICE4_BIT		1 << 4
	.define VOICE5_BIT		1 << 5
	.define VOICE6_BIT		1 << 6
	.define VOICE7_BIT		1 << 7
	.define ALL_VOICES		$FF
