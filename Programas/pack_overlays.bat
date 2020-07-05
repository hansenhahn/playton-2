echo off

@echo Calling tl_overlay.py to update overlay table...
pypy tl_overlay.py -s0 "../Arquivos Gerais/y9.bin" -s1 "../Arquivos Gerais/overlay_0002.bin" -n 2
pypy tl_overlay.py -s0 "../Arquivos Gerais/y9.bin" -s1 "../Arquivos Gerais/overlay_0011.bin" -n 11
pypy tl_overlay.py -s0 "../Arquivos Gerais/y9.bin" -s1 "../Arquivos Gerais/overlay_0019.bin" -n 19
pypy tl_overlay.py -s0 "../Arquivos Gerais/y9.bin" -s1 "../Arquivos Gerais/overlay_0023.bin" -n 23
pypy tl_overlay.py -s0 "../Arquivos Gerais/y9.bin" -s1 "../Arquivos Gerais/overlay_0027.bin" -n 27