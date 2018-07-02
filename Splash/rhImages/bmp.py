#!/usr/bin/env python
# -*- coding: utf-8 -*-

# images/bmp.py

# Copyright 2009-2010 Diego Hansen Hahn (aka DiegoHH) <diegohh90 [at] hotmail [dot] com>

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
	Módulo simples para criação e leitura de arquivos BMP
'''

__author__ = "Diego Hansen Hahn"
__version__ = "v2.0.2"

import struct
import array
from math import ceil

FILE_HEADER_TYPE = 'BM'
FILE_HEADER_SIZE = 54
FILE_HEADER_RESERVED = 0
FILE_HEADER_OFFSET_BITS = 54
INFO_HEADER_SIZE = 40
INFO_HEADER_PLANES = 1
#INFO_HEADER_BITCOUNT
INFO_HEADER_COMPRESSION = 0
INFO_HEADER_X_PIXELS_PER_METER = 0
INFO_HEADER_Y_PIXELS_PER_METER = 0
#INFO_HEADER_COLORS_USED
#INFO_HEADER_COLORS_IMPORTANT

class Reader:
	def __init__(self, _guess):
		if isinstance(_guess, str):
			self.file = open(_guess, 'rb')
		elif isinstance(_guess, file):
			self.file = _guess
		else:
			raise TypeError('expecting filename or file.')

		self.infoheader = {}
		self.fileheader = {}
		self.data = []

	def read_header(self):
		self.file.seek(0,0)

		self.fileheader['signature'] = self.file.read(2)
		self.fileheader['filesize'] = struct.unpack('<L', self.file.read(4))[0]
		self.file.read(4) # Reservado... não é usado
		self.fileheader['dataoffset'] = struct.unpack('<L', self.file.read(4))[0]

		self.infoheader['size'] = struct.unpack('<L', self.file.read(4))[0]
		self.infoheader['width'] = struct.unpack('<L', self.file.read(4))[0]
		self.infoheader['height'] = struct.unpack('<L', self.file.read(4))[0]
		self.infoheader['planes'] = struct.unpack('<H', self.file.read(2))[0]
		self.infoheader['bitdepth'] = struct.unpack('<H', self.file.read(2))[0]
		self.infoheader['compression'] = struct.unpack('<L', self.file.read(4))[0]
		self.infoheader['imagesize'] = struct.unpack('<L', self.file.read(4))[0]
		self.infoheader['xpixelsm'] = struct.unpack('<L', self.file.read(4))[0]
		self.infoheader['ypixelsm'] = struct.unpack('<L', self.file.read(4))[0]
		self.infoheader['colorsused'] = struct.unpack('<L', self.file.read(4))[0]
		self.infoheader['colorsimportant'] = struct.unpack('<L', self.file.read(4))[0]

	def read_palette(self):
		def rgbtuple(data):
			red = data >> 16 & 0xFF
			green = data >> 8 & 0xFF
			blue = data & 0xFF
			return (red, green, blue)

		if not (self.fileheader and self.infoheader):
			self.read_header()

		if self.fileheader['signature'] != 'BM':
			raise TypeError('this file is not a bmp file.')

		self.bitdepth = self.infoheader['bitdepth']

		if self.bitdepth > 8:
			raise ValueError('bitmaps with bitdepth greater than 8 doesn\'t have palette.')

		self.file.seek(0x36, 0)
		color_palette = []
		for x in range(2**self.bitdepth):
			color_palette.append(struct.unpack('<L', self.file.read(4))[0])
		# Converter para tuplas R, G, B
		color_palette = map(rgbtuple, color_palette)

		return color_palette

	def read(self):
		if not (self.fileheader and self.infoheader):
			self.read_header()

		if self.fileheader['signature'] != 'BM':
			raise TypeError('this file is not a bmp file.')

		self.bitdepth = self.infoheader['bitdepth']

		if self.infoheader['compression']:
			return TypeError('compressed bitmaps are not supported yet.')

		if self.data:
			self.data = []

		self.file.seek(self.fileheader['dataoffset'], 0)
		if self.bitdepth <= 8:
			if self.bitdepth < 8:
				sample = 8/self.bitdepth
				mask = 2**self.bitdepth-1
				shift = [x * self.bitdepth for x in reversed(range(sample))]
			height = self.infoheader['height']
			width = self.infoheader['width'] / (8/self.bitdepth)
			for x in range(height):
				row = []
				for y in range(width):
					pixel = struct.unpack('B', self.file.read(1))[0]
					if self.bitdepth < 8:
						row += [mask & (pixel >> i) for i in shift]
					else:
						row.append(pixel)
				if width % 4 != 0:
					self.file.read(4 - (width % 4))
				self.data.append(row)
		elif self.bitdepth == 16:
			return TypeError('bitdepth 16 not supported yet')
		elif self.bitdepth == 24:
			height = self.infoheader['height']
			width = self.infoheader['width']
			for x in range(height):
				row = []
				for y in range(width):
					blue = struct.unpack('B', self.file.read(1))[0]
					green = struct.unpack('B', self.file.read(1))[0]
					red = struct.unpack('B', self.file.read(1))[0]
					row.append((red, green, blue))
				self.data.append(row)

		self.data = list(reversed(self.data))
		return self.data

	def read_as_rgb(self):
		if not self.data:
			self.data = self.read()

		if self.bitdepth == 24:
			return self.data

		color_palette = self.read_palette()
		rgb_data = map(lambda row: map(color_palette.__getitem__, row), self.data)

		return rgb_data


class Writer:
	def __init__(self, width, height, bitdepth, size = None, palette = None):
		if size:
			if len(size) != 2:
				raise ValueError('size should be (width, height)')
			else:
				self.width = size[0]
				self.height = size[1]
		else:
			self.width = width
			self.height = height

		if self.width <= 0 or self.height <= 0:
			raise ValueError('width and height must be greater than 0')

		if bitdepth > 8:
			if palette:
				raise ValueError('with palette, bitdepth should be 1,2,4 or 8')
		else:
			if len(palette) != 2**bitdepth:
				raise ValueError('palette lenght should be equal to 2^bitdepth')

		self.palette = palette
		self.bitdepth = bitdepth
		if self.bitdepth <= 8:
			self.bwidth = self.width * self.bitdepth / 8
		elif self.bitdepth == 24:
			self.bwidth = self.width * 3

	def write(self, outfile, row_buffer):
		entries = 2**self.bitdepth if self.bitdepth <= 8 else 0

		# Escreve o header do arquivo
		outfile.write(FILE_HEADER_TYPE)
		outfile.write(struct.pack('<L', FILE_HEADER_SIZE + (self.bwidth + (4 - self.bwidth % 4)) * self.height + 4 * entries))
		outfile.write(struct.pack('<L', FILE_HEADER_RESERVED))
		outfile.write(struct.pack('<L', FILE_HEADER_OFFSET_BITS + 4 * entries))
		outfile.write(struct.pack('<L', INFO_HEADER_SIZE))
		outfile.write(struct.pack('<L', self.width))
		outfile.write(struct.pack('<L', self.height))
		outfile.write(struct.pack('<H', INFO_HEADER_PLANES))
		outfile.write(struct.pack('<H', self.bitdepth))
		outfile.write(struct.pack('<L', INFO_HEADER_COMPRESSION))
		outfile.write(struct.pack('<L', (self.bwidth + (4 - self.bwidth % 4)) * self.height))
		outfile.write(struct.pack('<L', INFO_HEADER_X_PIXELS_PER_METER))
		outfile.write(struct.pack('<L', INFO_HEADER_Y_PIXELS_PER_METER))
		outfile.write(struct.pack('<L', entries))
		outfile.write(struct.pack('<L', 0))

		# Escreve a paleta de cores no arquivo
		if self.bitdepth <= 8:
			for color in self.palette:
				color = map(int, color)
				color = (color[0] << 16 | color[1] << 8 | color[2]) & 0xFFFFFF
				outfile.write(struct.pack('<L', color))

		# Hora de escrever os dados
		row_buffer = reversed(row_buffer)

		if self.bitdepth < 8:
			samples = 8/self.bitdepth

		data = array.array('B')
		for lines in row_buffer:
			if self.bitdepth < 8:
				lines = zip(*[iter(lines)]*samples) # Agrupa por amostragem
				lines = map(lambda e: reduce(lambda x,y:(x << self.bitdepth) + y, e), lines) # Converte o grupo de amostragem para 1 byte
				while len(lines) % 4 != 0:
					lines.append(0)
				data.extend(lines)
			elif self.bitdepth == 8:
				while len(lines) % 4 != 0:
					lines.append(0)
				data.extend(lines)
			elif self.bitdepth == 24:
				lines = map(lambda x: list(reversed(x)), lines)
				for pixel in lines:
					data.extend(pixel)

		data.tofile(outfile)

		return True