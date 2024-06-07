AS=wla-65816
LD=wlalink
BMP2CHR=bmp2chr
PACKER=packer
ROM=game

COBJ=game.obj

all: graphics encodings $(ROM).smc
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
	rm -f $(ROM).smc $(COBJ) 
