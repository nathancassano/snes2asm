PREFIX=~/snes-sdk
OPTIMIZE=1

CFLAGS=-Wall
ifeq ($(OPTIMIZE),1)
CFLAGS += -O
endif

BINDIR=$(PREFIX)/bin
AS=$(BINDIR)/wla-65816
LD=$(BINDIR)/wlalink
CC=$(BINDIR)/816-tcc
LIBDIR=$(PREFIX)/lib
ROM=game

COBJ=game.obj

all: $(ROM).smc
	echo "Done"

$(ROM).smc: $(COBJ)
	$(LD) -dvSo $(COBJ) $(ROM).smc

%.s: %.c
	$(CC) $(CFLAGS) -I. -o $@ -c $<

%.obj: %.s
	$(AS) -io $< $@

clean:
	rm -f $(ROM).smc $(ROM).sym $(COBJ) *.s
