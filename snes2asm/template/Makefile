AS=wla-65816
AS_SPC700=wla-spc700
LD=wlalink
BMP2CHR=bmp2chr
PACKER=packer
BRR=brr
ROM=game
COBJ=game.o

all: graphics sound spc700 encodings $(ROM).smc
	echo "Done"

.PHONY: graphics
graphics: $(patsubst %.bmp,%.chr,$(wildcard *2bpp.bmp *3bpp.bmp *4bpp.bmp *8bpp.bmp))

%2bpp.chr: %2bpp.bmp
	$(BMP2CHR) -b2 -o $@ $<

%3bpp.chr: %3bpp.bmp
	$(BMP2CHR) -b3 -o $@ $<

%4bpp.chr: %4bpp.bmp
	$(BMP2CHR) -b4 -o $@ $<

%8bpp.chr: %8bpp.bmp
	$(BMP2CHR) -b8 -o $@ $<

.PHONY: sound
sound: *.brr

%.brr: %.wav
	$(BRR) encode -o $@ $<

.PHONY: spc700
spc700: $(patsubst %.S,%.spc,$(wildcard *.S))

# Compile SPC700 assembly to object file
%.obj: %.S
	$(AS_SPC700) -i -o $@ $<

# Link SPC700 object file to binary
%.spc: %.obj
	$(LD) -i -S linkfile_spc $@

.PHONY: encodings
encodings: %encode_files

%endcode_targets

main.s: *.asm
	touch main.s

$(COBJ): *.s
	$(AS) -x -v -o $@ $<

$(ROM).smc: $(COBJ)
	$(LD) -d -v -S linkfile $(ROM).smc

clean:
	rm -f $(ROM).smc $(COBJ) *.obj *.o *.linkfile
