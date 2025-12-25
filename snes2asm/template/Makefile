AS=wla-65816
AS_SPC700=wla-spc700
LD=wlalink
BMP2CHR=bmp2chr
PACKER=packer
BRR=brr
ROM=game

COBJ=game.obj
SOBJ=spc700.o

all: graphics encodings sound spc700 $(ROM).smc
	echo "Done"

.PHONY: graphics
graphics: *2bpp.chr *3bpp.chr *4bpp.chr *8bpp.chr

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
spc700: *.bin

${SOBJ}: %.spc
	$(AS_SPC700) -o $@ $<

%.bin: ${COBJ}
	$(LD) -b linkfile_spc $@

.PHONY: encodings
encodings: %encode_files

%endcode_targets
%.s: *.asm
	touch $@

$(COBJ): *.s
	$(AS) -x -v -o $@ $<

$(ROM).smc: $(COBJ)
	$(LD) -d -v -S linkfile $(ROM).smc

%::
	@echo -n

clean:
	rm -f $(ROM).smc $(COBJ) *.bin *.obj 
