@echo off

echo "Layton's Assembler by DiegoHH"

rem Copia alguns arquivos "estratégicos" para a pasta com a Rom Modificada
copy "Arquivos Gerais\overlay9_0002.bin" "ROM Modificada\PLAYTON2\overlay" /B/Y

REM rem Arquivos copiados do espanhol, pelo fato de serem maiores ou terem a paleta de cores modificada
REM copy "ROM Original\PLAYTON\data\data\ani\es\jiten_num.arc" "ROM Modificada\PLAYTON\data\data\ani\en\jiten_num.arc" /B/Y
REM copy "ROM Original\PLAYTON\data\data\ani\es\story_gfx.arc" "ROM Modificada\PLAYTON\data\data\ani\en\story_gfx.arc" /B/Y
REM copy "ROM Original\PLAYTON\data\data\ani\es\story_page_buttons.arc" "ROM Modificada\PLAYTON\data\data\ani\en\story_page_buttons.arc" /B/Y
copy "ROM Original\PLAYTON2_ES\data\data_lt2\ani\menu\bag\sp\memo_close_buttons.arc" "ROM Modificada\PLAYTON2\data\data_lt2\ani\menu\bag\en\memo_close_buttons.arc" /B/Y
copy "ROM Original\PLAYTON2_ES\data\data_lt2\ani\system\btn\sp\cancel.arc" "ROM Modificada\PLAYTON2\data\data_lt2\ani\system\btn\en\cancel.arc" /B/Y



rem Copia os arquivos de fonte
copy "Fontes\font18.NFTR" "ROM Modificada\PLAYTON2\data\data_lt2\font" /B/Y
copy "Fontes\fontevent.NFTR" "ROM Modificada\PLAYTON2\data\data_lt2\font" /B/Y
copy "Fontes\fontq.NFTR" "ROM Modificada\PLAYTON2\data\data_lt2\font" /B/Y

rem Executa os packers de imagem e texto
cd Programas
call pack_images.bat
call pack_texts.bat
cd ..

rem Executa o gerador de splash
rem copy "Splash\arm9.bin" "ROM Modificada\PLAYTON" /B/Y

rem Monta a ROM nova e gera um patch
cd ROM Modificada
call pack_rom.bat
call do_patch.bat
cd ..