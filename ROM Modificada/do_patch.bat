@echo off

REM xdelta.exe -efs "..\ROM Original\4215 - Professor Layton and Pandora's Box (EU)(BAHAMUT).nds" "4215 - Professor Layton and Pandora's Box (BR)(BAHAMUT).nds" "playton-2.xdelta"

xdelta.exe -B 134217728 -e -9 -S djw -vfs "..\ROM Original\4215 - Professor Layton and Pandora's Box (EU)(BAHAMUT).nds" "4215 - Professor Layton and Pandora's Box (BR)(BAHAMUT).nds" "playton-2.xdelta"