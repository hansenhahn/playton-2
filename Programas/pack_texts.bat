@echo off

echo "Calling tl_dumper.py to pack plz text"
pypy tl_dumper.py -m i -s "../Textos Traduzidos/plz" -d "../ROM Modificada/PLAYTON2/data/data_lt2"

echo "Calling tl_dumper_rc.py to pack dlz text"
pypy tl_dumper_rc.py -m i -s "../Textos Traduzidos/dlz" -d "../ROM Modificada/PLAYTON2/data/data_lt2"
