PREFIX=~/snes-sdk

BINDIR=$(PREFIX)/bin
AS=$(BINDIR)/wla-65816
LD=$(BINDIR)/wlalink
BMP2CHR=~/snes2asm/bin/bmp2chr
ROM=game

COBJ=game.obj

all: graphics $(ROM).smc
	echo "Done"

.PHONY: graphics
graphics: *2bpp.chr *4bpp.chr *8bpp.chr

%2bpp.chr: %2bpp.bmp
	$(BMP2CHR) -b2 -o $@ $<

%4bpp.chr: %4bpp.bmp
	$(BMP2CHR) -b4 -o $@ $<

%8bpp.chr: %8bpp.bmp
	$(BMP2CHR) -b8 -o $@ $<

$(COBJ): *.s
	$(AS) -v -o $@ $<

$(ROM).smc: $(COBJ)
	$(LD) -d -v -S linkfile $(ROM).smc

%::
	@echo -n

clean:
	rm -f $(ROM).smc $(COBJ) 
