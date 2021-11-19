PREFIX=~/snes-sdk

BINDIR=$(PREFIX)/bin
AS=$(BINDIR)/wla-65816
LD=$(BINDIR)/wlalink
ROM=game

COBJ=game.obj

all: $(ROM).smc
	echo "Done"

$(COBJ): *.s
	$(AS) -o $@ $<

$(ROM).smc: $(COBJ)
	$(LD) -dvSo $(COBJ) $(ROM).smc

clean:
	rm -f $(ROM).smc $(COBJ) 
