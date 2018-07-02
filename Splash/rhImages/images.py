#!/usr/bin/env python
# -*- coding: utf-8 -*-

# images/images.py

# Copyright 2009-2010 Diego Hansen Hahn (aka DiegoHH) <diegohh90 [at] hotmail [dot] com>

# png.py - PNG encoder/decoder in pure Python
#
# Copyright (C) 2006 Johann C. Rocholl <johann@browsershots.org>
# Portions Copyright (C) 2009 David Jones <drj@pobox.com>
# And probably portions Copyright (C) 2006 Nicko van Someren <nicko@nicko.org>
#
# Original concept by Johann C. Rocholl.

# lazynds is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License.

# lazynds is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with lazynds. If not, see <http://www.gnu.org/licenses/>.

'''
    Módulo responsável por ler e criar as imagens dos buffers.
'''

__author__ = "Diego Hansen Hahn"
__version__ = "v2.0.2"

from math import ceil
import struct
import array

import bmp
#import png

#import quantize

#import timedebugger

def Quantize(pixels, max_color):
    cube = quantize.Cube(pixels, max_color)
    cube.classification()
    cube.reduction()
    cube.assignment()
    return (cube.image, cube.colormap)

class Reader:
    def __init__(self, _guess):
        if isinstance(_guess, str):
            self.file = open(_guess, 'rb')
        elif isinstance(_guess, file):
            self.file = _guess
        else:
            raise TypeError('expecting filename or file')

    def read(self, mode, bitdepth):
        self.file.seek(0,0)
        # As funções de leitura não possuem dados de retorno igual, por isso são processadas separadamente
        if self.file.name.split('.')[-1].lower() == 'png':
            w = png.Reader(self.file)
            data_tuple = w.read()
            metadata = data_tuple[3]
            if metadata['bitdepth'] == 8 and bitdepth == 8:
                #Tenta ler a paleta
                try:
                    self.data = list(data_tuple[2])
                    self.colormap = w.palette()
                except:
                    # ???
                    self.file.seek(0,0)
                    w = png.Reader(self.file)
                    flat = list(w.asRGBA8()[2])
                    boxed = [zip(*[iter(row)]*4) for row in flat]
                    self.data, self.colormap = Quantize(boxed, 2**bitdepth)
            elif metadata['bitdepth'] > bitdepth: # Há mais cores que o suportado..
                flat = list(w.asRGBA8()[2]) # Gera um arquivo RGBA
                # O retorno é do tipo [R,G,B,A , R,G,B,A ..]
                # Convertendo para [(R,G,B,A),(R,G,B,A)...]
                # O A é ignorado na hora da redução de cores
                boxed = [zip(*[iter(row)]*4) for row in flat]
                self.data, self.colormap = Quantize(boxed, 2**bitdepth)
            else:
                self.data = list(data_tuple[2])
                self.colormap = w.palette()
        elif self.file.name.split('.')[-1].lower() == 'bmp':
            w = bmp.Reader(self.file)
            w.read_header()
            if w.infoheader['bitdepth'] > bitdepth:
                self.data, self.colormap = Quantize(w.read_as_rgb(), 2**bitdepth)
            else:
                self.data = w.read()
                self.colormap = w.read_palette()
        else:
            raise TypeError('file is neither bmp nor png.')

        self.colormap.extend(zip(*[iter((0,0,0) * (2**bitdepth - len(self.colormap)))] * 3))

        return self.data, self.colormap

    def as_data(self, mode, bitdepth, palette = None):
        if not hasattr(self, "data"):
            self.read(mode, bitdepth)

        bitarray = array.array('B')

        # if palette != self.colormap:
            # for row in self.data:
                # for x in range(len(row)):
                    # row[x] = palette.index(self.colormap[row[x]])

            # self.colormap = palette

        sample = 8/bitdepth
        if mode == 1:
            # Gera um buffer com tantos tiles quanto necessário:
            width_tiles = (len(self.data[0]) / bitdepth)
            height_tiles = (len(self.data) / 8)

            tiles_buffer = [[list() for x in range(width_tiles+1)] for y in range(height_tiles+1)]

            height = 0
            count = 0
            for row in self.data:
                tiles_row = tiles_buffer[count]
                # Junta as amostras
                if bitdepth < 8:
                    row = zip(*[iter(row)]*sample)
                    row = map(lambda e: reduce(lambda x,y:(x << bitdepth) + y, reversed(e)), row)
                number = 0
                for tile in tiles_row:
                    tile += row[(number*bitdepth):((number+1)*bitdepth)]
                    number += 1
                height += 1
                if height == 8:
                    height = 0
                    count += 1

            for x in tiles_buffer:
                for y in x:
                    bitarray.extend(y)

        elif mode == 2:
            for row in self.data:
                if bitdepth < 8:
                    row = zip(*[iter(row)]*sample)
                    row = map(lambda e: reduce(lambda x,y:(x << bitdepth) + y, reversed(e)), row)
                bitarray.extend(row)

        else:
            raise ValueError('mode can be only 1 or 2.')

        return array.array('c', bitarray.tostring()), self.colormap[:2**bitdepth]


class Writer:
    def __init__(self, size, palette, bitdepth, mode, alpha = False):
        self.width, self.height = size
        self.mode = mode
        self.bitdepth = bitdepth
        self.alpha = alpha

        self.palette = []

        # canal alpha informado externamente
        #self.alpha_channel = map(lambda x: int(bool(x % 2**self.bitdepth)), range(256))

        w = 0
		
        for color in palette:
            if self.alpha:
                r = color[0]; g = color[1]; b = color[2]; alpha = color[3]
            else:
                r = color[0]; g = color[1]; b = color[2];

            if isinstance(r, float):
                if self.alpha:
                    self.palette.append((ceil(r * 0xFF), ceil(g * 0xFF), ceil(b * 0xFF), ceil(alpha * 0xFF)))
                else:
                    self.palette.append((ceil(r * 0xFF), ceil(g * 0xFF), ceil(b * 0xFF)))
            else:
                if self.alpha:
                    self.palette.append((r, g, b, alpha))
                else:
                    self.palette.append((r, g, b))

    def write(self, outfile, buffer, bitdepth, extension):

        buffer = array.array('c', buffer)
        size = self.width * self.height / (8/self.bitdepth)
        # Adiciona os bytes extras para deixar o buffer do tamanho previsto
        padding = size - len(buffer)
        buffer.extend('\x00' * padding)


        # Converte o buffer para o formato [[ROW 1],[ROW 2],..[ROW N]] .. de acordo com o PyPNG
        row_buffer = []

        if self.bitdepth < 8:
            sample = 8/self.bitdepth
            mask = 2**self.bitdepth-1
            shift = [x * self.bitdepth for x in range(sample)]
        total = len(buffer)/(self.bitdepth * 8)

        if self.mode == 1:
            width = self.width / 8
            for x in range(0, total, width):
                for y in range(8):
                    row = []
                    for z in range(width):
                        pos = (x + z)*(self.bitdepth*8)
                        line = buffer[pos+self.bitdepth*y:pos+self.bitdepth*(y+1)]
                        for c in line:
                            c = struct.unpack('B', c)[0]
                            if self.bitdepth < 8:
                                row += [mask & (c >> i) for i in shift]
                            else:
                                row.append(c)
                    row_buffer.append(row)
        elif self.mode == 2:
            for x in range(self.height):
                row = []
                pos = ((self.width + self.width % (8/self.bitdepth))/ (8/self.bitdepth))    # Não será usada uma vez que queremos que a
                #                                                                              imagem sempre tenha largura múltiplo de 8
                #line = buffer[x*(self.width*self.bitdepth):(x+1)*(self.width*self.bitdepth)]
                line = buffer[x*pos:(x+1)*pos]
                for c in line:
                    c = struct.unpack('B', c)[0]
                    if self.bitdepth < 8:
                        row += [mask & (c >> i) for i in shift]
                    else:
                        row.append(c)
                row_buffer.append(row)

        # Internamente, o lazy sempre mostrará as imagens em 8bpp
        if self.alpha:
            self.palette.extend(zip(*[iter((0,0,0,0) * (2**bitdepth - len(self.palette)))] * 4))
        else:
            self.palette.extend(zip(*[iter((0,0,0) * (2**bitdepth - len(self.palette)))] * 3))

        if extension == 'PNG':
            w = png.Writer(len(row_buffer[0]), len(row_buffer), palette=self.palette, bitdepth=bitdepth)
            w.write(outfile, row_buffer)
        elif extension == 'BMP':
            w = bmp.Writer(len(row_buffer[0]), len(row_buffer), palette=self.palette, bitdepth=bitdepth)
            w.write(outfile, row_buffer)

        return padding