#!/usr/bin/env python
# -*- coding: utf-8 -*-

import array
import os
import shutil
import struct
import sys
import tempfile
import math

from rhImages import images

#import psyco
#psyco.full()
def tuple2gba(r, g, b, a=None):
    rgb = ((int( math.ceil(b/255.0*31)) << 10) | (int( math.ceil(g/255.0*31)) << 5) | int( math.ceil(r/255.0*31)) ) & 0x7FFF
    return struct.pack('<H', rgb)

def search(pattern, text):
    ''' Baseado no algoritmo de Boyer-Moore-Horspool portado para python por Nelson Rush '''
    m = len(pattern)
    n = len(text)
    if m > n:
        return -1
    skip = []
    for k in range(256):
        skip.append(m)
    for k in range(m - 1):
        skip[ord(pattern[k])] = m - k - 1
    skip = tuple(skip)
    k = m - 1
    while k < n:
        j = m - 1
        i = k
        while j >= 0 and text[i] == pattern[j]:
            j -= 1
            i -= 1
        if j == -1 and (i + 1) % 2 == 0:
        # Modificação feita para retornar ocorrências apenas que se encontram em uma posição par no buffer
            return (i + 1 + 2, m)
        k += skip[ord(text[k])]
    return -1
    
def insert():
    # if not os.path.isdir('Input'):
        # return
        
    input = open( "Splash.bmp", "rb" )
    w = images.Reader( input )
    data, colormap = w.as_data(mode = 2, bitdepth = 8)
    input.close()
    
    infile = open('splash_raw.bin', 'wb')
    for color in colormap:
        infile.write( tuple2gba( *color ) )
        
    infile.seek( 0x400 )
    data.tofile(infile)
    infile.close()
    
    # shutil.copy(file, 'Yggdra Modificado.gba')
    # file = open('Yggdra Modificado.gba', 'r+b')
    file = open('splash_c.bin', 'wb')
    
    # for name in os.listdir('Input'):
        # input = open('Input/'+name, 'rb')
        # w = images.Reader(input)
        # data, colormap = w.read(mode = 1, bitdepth = 4)
        # data, colormap = w.as_data(mode = 1, bitdepth = 4, palette = colormap)
        # input.close()
        
        # infile = tempfile.NamedTemporaryFile()
        # data.tofile(infile.file)
    infile = open('splash_raw.bin', 'rb')

    sliding_window = array.array('c')
    data_buffer = array.array('c')
    header_buffer = array.array('c')
    buffer_1 = array.array('c') # Buffer de pesquisa                aka "from RAM"
    buffer_2 = array.array('c') # Buffer de dados sem ocorrência    aka "from ROM"

    infile.seek(0, 0)

    while infile.tell() < os.path.getsize(infile.name):
        for x in infile.read(2):
            buffer_1.insert(0, x)
        # Busca esses dados no buffer cíclico - sliding_window - !
        s_result = search(buffer_1, sliding_window[2:])
        if s_result == -1:
            # Confere se o buffer é menor ou igual a 6
            # Manda os 2 primeiros bytes do buffer - como é invertido os 2 ultimos
            # para o buffer de ROM e volta 2 posições na ROM
            if len(buffer_1) <= 4:
                if len(buffer_1) == 4:
                    infile.seek(-2,1)
                buffer_2.append(buffer_1.pop(-1))
                buffer_2.append(buffer_1.pop(-1))
                sliding_window.insert(0,buffer_2[-2])
                sliding_window.insert(0,buffer_2[-1])
                buffer_1 = array.array('c')
                # Confere se buffer_2 já atingiu tamanho máximo
                # Se sim, é adicionado ao buffer de dados e montado o par de compressão
                if len(buffer_2) == 65534:
                    header = len(buffer_2) >> 1
                    header_buffer.extend(struct.pack('<H', header))
                    # Adicionar buffer_2 a data buffer
                    for x in buffer_2:
                        data_buffer.append(x)                       
                    buffer_2 = array.array('c')
            # Senão, o buffer é considerado válido
            # porém, os 2 últimos bytes lidos são descartados e volta
            # 2 posições na ROM
            else:
                buffer_1.pop(0)
                buffer_1.pop(0)
                infile.seek(-2, 1)
                
                wordCount = (settings[1] >> 1) - 2
                ramDistance = (settings[0] + settings[1]) >> 1
                
                header = ((wordCount << 0x0a) | ramDistance | 0x8000) & 0xFFFF
                header_buffer.extend(struct.pack('<H', header))
                # Monta o par de compressão
                # Adicionar buffer_1 a sliding_window
                for x in buffer_1[::-1]:
                    sliding_window.insert(0,x)                  
                buffer_1 = array.array('c')
                
        else:
            settings = s_result
            # Verifica se o buffer de pesquisa já é maior que 6
            # Caso verdadeiro, podemos já adicionar o buffer_2 (se existir) ao buffer de dados
            # e reiniciá-lo
            if len(buffer_1) >= 4 and buffer_2:
                    # Adicionar buffer_2 a data buffer
                    header = len(buffer_2) >> 1
                    header_buffer.extend(struct.pack('<H', header))

                    for x in buffer_2:
                        data_buffer.append(x)
                    buffer_2 = array.array('c')                     
            # Confere se o buffer de pesquisa já atingiu seu tamanho máximo
            if len(buffer_1) == 66:
                wordCount = (settings[1] >> 1) - 2
                ramDistance = (settings[0] + settings[1]) >> 1
                
                header = ((wordCount << 0x0a) | ramDistance | 0x8000) & 0xFFFF
                header_buffer.extend(struct.pack('<H', header))

                for x in buffer_1[::-1]:
                    sliding_window.insert(0,x)
                buffer_1 = array.array('c')                 

        while len(sliding_window) > 2046:
            sliding_window.pop()

    infile.close()
    
    #file.seek(OFF_TESTE, 0)
    

    file.write(struct.pack('<H', len(header_buffer) >> 1))
    header_buffer.tofile(file)
    data_buffer.tofile(file)
    # buffer.tofile(file)
    
    #file.seek(pointers[2], 0)
    #file.write(struct.pack('<L', 0x9fe3760))

    file.close()

    return


if __name__ == '__main__':

    print 'Comprimindo splash...'
    
    #opt = int(raw_input('\n[1] Extrair Imagens \n[2] Inserir Imagens (Teste) \n[3] Sair \n'))
    
    # if opt == 1:
        # extract()
        # sys.exit(1)
    # elif opt == 2:
    insert()
    sys.exit(1)
    # elif opt == 3:
        # sys.exit(1)

