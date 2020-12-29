@echo off

del "4215 - Professor Layton and Pandora's Box (BR)(BAHAMUT).nds"
cd PLAYTON2
..\ndstool -c "..\4215 - Professor Layton and Pandora's Box (BR)(BAHAMUT).nds" -9 arm9.bin -7 arm7.bin -y9 y9.bin -y7 y7.bin -d data -y overlay -t banner.bin -h header.bin
cd ..

