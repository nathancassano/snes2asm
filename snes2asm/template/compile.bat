@rem compile C code only, without recompiling resources
@echo off

set relname="game.sfc"

set path=tools\bin;tools

REM C -> ASM / S

del game.s  2>nul
del game.s1 2>nul
del game.s2 2>nul

816-tcc.exe -Wall -Itools/include -o game.s -c game.c

rem pause

REM Optimize ASM files

816-opt.py game.s > game.s1

goto optlev1

:optlev1

ren game.s1 game.s2
goto optdone

:optlev2

optimore-816.exe game.s1 game.s2

:optdone

REM ASM -> OBJ

wla-65816.exe -io game.s2 game.obj

REM OBJ -> SMC

wlalink.exe -sdvSo game.obj %relname%

pause

REM delete files

del *.s   2>nul
del *.s1  2>nul
del *.s2  2>nul
del *.obj 2>nul
del *.sym 2>nul
del stderr.txt 2>nul
del stdout.txt 2>nul
del *.wla* 2>nul
