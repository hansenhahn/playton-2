@echo Monkeys Traduções

@echo "Calling tl_img.py to unpack background"
pypy tl_img.py -m e0 -s "../ROM Original/PLAYTON2_IT/data/data_lt2" -d "../Imagens Originais/it"

echo "Calling tl_img.py to unpack animation"
pypy tl_img.py -m e1 -s "../ROM Original/PLAYTON2_IT/data/data_lt2" -d "../Imagens Originais/it"