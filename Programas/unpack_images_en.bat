@echo Monkeys Traduções

@echo "Calling tl_img.py to unpack background"
python tl_img.py -m e0 -s "../ROM Original/Splitted/LAYTON2/data_lt2" -d "../Imagens Originais"

echo "Calling tl_img.py to unpack animation"
python tl_img.py -m e1 -s "../ROM Original/Splitted/LAYTON2/data_lt2" -d "../Imagens Originais"

pause