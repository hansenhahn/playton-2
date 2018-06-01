@echo off

armips.exe arm9.asm
rem blz.exe -en9 arm9.bin

armips.exe overlay_0019_novo.asm
blz.exe -en overlay_0019.bin

armips.exe overlay_0023_novo.asm
blz.exe -en overlay_0023.bin

copy "overlay_0002_nocompression.bin" "overlay_0002.bin" /B/Y
blz.exe -en overlay_0002.bin

copy "arm9.bin" "..\Arquivos Gerais" /B/Y
copy "overlay_0019.bin" "..\Arquivos Gerais" /B/Y
copy "overlay_0023.bin" "..\Arquivos Gerais" /B/Y
copy "overlay_0002.bin" "..\Arquivos Gerais" /B/Y