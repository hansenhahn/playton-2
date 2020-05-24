echo off

@echo Calling tl_img.py to pack background
pypy tl_img.py -m i0 -s "../Imagens Traduzidas" -d "../ROM Modificada/PLAYTON2/data/data_lt2"

@echo Calling tl_img.py to pack animation
pypy tl_img.py -m i1 -s "../Imagens Traduzidas" -d "../ROM Modificada/PLAYTON2/data/data_lt2" -s1 "../ROM Modificada/PLAYTON2/data/data_lt2"