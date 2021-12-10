PREFIX=~/snes-sdk

BINDIR=$(PREFIX)/bin
AS=$(BINDIR)/wla-65816
LD=$(BINDIR)/wlalink
ROM=game

COBJ=game.obj

all: $(ROM).smc
	echo "Done"

$(COBJ): *.s
	$(AS) -v -o $@ $<

$(ROM).smc: $(COBJ)
	$(LD) -d -v -S linkfile $(ROM).smc

clean:
	rm -f $(ROM).smc $(COBJ) 
