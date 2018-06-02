@echo off

echo "Layton's Assembler by DiegoHH"

REM rem Arquivos copiados do espanhol, ou alterados o original, pelo fato de serem maiores ou terem a paleta de cores modificada
copy "ROM Original\PLAYTON2_ES\data\data_lt2\ani\menu\bag\sp\memo_close_buttons.arc" "ROM Modificada\PLAYTON2\data\data_lt2\ani\menu\bag\en\memo_close_buttons.arc" /B/Y
copy "ROM Original\PLAYTON2_ES\data\data_lt2\ani\menu\secret\sp\modoru_btn.arc" "ROM Modificada\PLAYTON2\data\data_lt2\ani\menu\secret\en\modoru_btn.arc" /B/Y
copy "ROM Original\PLAYTON2_ES\data\data_lt2\ani\menu\secret\sp\secret_modoru.arc" "ROM Modificada\PLAYTON2\data\data_lt2\ani\menu\secret\en\secret_modoru.arc" /B/Y
copy "ROM Original\PLAYTON2_ES\data\data_lt2\ani\system\btn\sp\cancel.arc" "ROM Modificada\PLAYTON2\data\data_lt2\ani\system\btn\en\cancel.arc" /B/Y
copy "ROM Original\PLAYTON2_ES\data\data_lt2\ani\subgame\camera\sp\modoru_btn.arc" "ROM Modificada\PLAYTON2\data\data_lt2\ani\subgame\camera\en\modoru_btn.arc" /B/Y
copy "ROM Original\PLAYTON2_ES\data\data_lt2\ani\subgame\photo\sp\album_modoru.arc" "ROM Modificada\PLAYTON2\data\data_lt2\ani\subgame\photo\en\album_modoru.arc" /B/Y
copy "Arquivos Gerais\continue.arc" "ROM Modificada\PLAYTON2\data\data_lt2\ani\title\en\continue.arc" /B/Y

rem Cria os overlays
cd Asm
call gen_overlay.bat
cd ..

rem Executa os packers de overlay, imagem e texto
cd Programas
call pack_overlays.bat
call pack_images.bat
call pack_texts.bat
cd ..

rem Copia os arquivos de fonte
copy "Fontes\font18.NFTR" "ROM Modificada\PLAYTON2\data\data_lt2\font" /B/Y
copy "Fontes\fontevent.NFTR" "ROM Modificada\PLAYTON2\data\data_lt2\font" /B/Y
copy "Fontes\fontq.NFTR" "ROM Modificada\PLAYTON2\data\data_lt2\font" /B/Y

rem Copia alguns arquivos "estratégicos" para a pasta com a Rom Modificada
copy "Arquivos Gerais\arm9.bin" "ROM Modificada\PLAYTON2" /B/Y
copy "Arquivos Gerais\banner.bin" "ROM Modificada\PLAYTON2" /B/Y
copy "Arquivos Gerais\y9.bin" "ROM Modificada\PLAYTON2" /B/Y
copy "Arquivos Gerais\overlay_0002.bin" "ROM Modificada\PLAYTON2\overlay" /B/Y
copy "Arquivos Gerais\overlay_0019.bin" "ROM Modificada\PLAYTON2\overlay" /B/Y
copy "Arquivos Gerais\overlay_0023.bin" "ROM Modificada\PLAYTON2\overlay" /B/Y

rem Executa o gerador de splash
rem copy "Splash\arm9.bin" "ROM Modificada\PLAYTON" /B/Y

rem Monta a ROM nova e gera um patch
cd ROM Modificada
call pack_rom.bat
call do_patch.bat
cd ..