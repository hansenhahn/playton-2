#!/usr/bin/env python
# -*- coding: utf-8 -*-

import array
import os
import shutil
import struct
import sys
import tempfile

# from images import images, palettes

#import psyco
#psyco.full()

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

# pointers =  [0x01b88b0, 0x01b8950, 0x01b9738, 0x01b8860, 0x01b8888, 0x01b88d8, 0x01b8900,
		 	# 0x01b8928, 0x01b8978, 0x01b89a0, 0x01b89c8, 0x01b89f0, 0x01b8a18, 0x01b8a40,
			# 0x01b8a68, 0x01b8a90, 0x01b8ab8, 0x01b8ae0, 0x01b8b08, 0x01b8b30, 0x01b8b58,
			# 0x01b8b80, 0x01b8ba8, 0x01b8bd0]

pointers = [1804384L, 1804424L, 1804464L, 1804504L, 1804544L, 1804584L, 1804624L, 1804664L,
			1804704L, 1804744L, 1804784L, 1804824L, 1804864L, 1804904L, 1804944L, 1804984L,
			1805024L, 1805064L, 1805104L, 1805144L, 1805184L, 1805224L, 1805264L, 1805304L,
			1805344L, 1805384L, 1805424L, 1805464L, 1805504L, 1805544L, 1805584L, 1805624L,
			1805664L, 1805704L, 1805744L, 1805784L, 1805824L, 1805864L, 1805904L, 1805944L,
			1805984L, 1806024L, 1806064L, 1806104L, 1806144L, 1806184L, 1806224L, 1806264L,
			1806304L, 1806344L, 1806384L, 1806424L, 1808184L, 1808204L, 1808224L, 1808244L,
			1808264L]
			
	
def extract(file = '2598 - Yggdra Union - We\'ll Never Fight Alone (U).gba'):
	if not os.path.isdir('Output'):
		os.mkdir('Output')

	# Gera a paleta
	colormap = palettes.Palette()
	colormap.generate_pal_from_extern(open('bg.pal', 'rb'))
	colormap.set_palette_mode(colormap.colors_extern)
	
	file = open(file, 'rb')
	
	for index in range(len(pointers)):
		file.seek(pointers[index], 0)
		
		file.seek(struct.unpack('<L', file.read(4))[0] & 0x1ffffff, 0)
		
		print 'Extraindo %08X...' %file.tell()

		output = array.array('c')
		
		currentIter = 0
		totalIter = struct.unpack('<H', file.read(2))[0]	
		
		headerAddress = file.tell()
		dataAddress = headerAddress + (totalIter << 1)		
		
		while currentIter <= totalIter:
			file.seek(headerAddress, 0)
			headerAddress += 2
			
			headerPar = struct.unpack('<H', file.read(2))[0]
			if headerPar & 0x8000:
				# Lê dados da RAM
				wordCount = (((headerPar >> 0x0a) & 0x1f) + 2)
				ramDistance = (headerPar & 0x3ff) << 1
				for x in range(wordCount << 1):
					output.append(output[len(output) - ramDistance])		
			else:
				# Lê dados da ROM
				file.seek(dataAddress, 0)
				wordCount = ((headerPar << 0x11) & 0xFFFFFFFF) >> 0x11
				
				output.extend(file.read(wordCount << 1))
				dataAddress += (wordCount << 1)
				
			currentIter += 1
			
		outfile = open('Output/%03d.bmp' % index, 'wb')
		w = images.Writer((28, len(output)/(32*28)), 4, colormap, False, 1)
		w.write(outfile, output, 4, 'BMP')				

	return	

OFF_TESTE = 0x1fe3760	
	
def insert(file = '2598 - Yggdra Union - We\'ll Never Fight Alone (U).gba'):
	# if not os.path.isdir('Input'):
		# return
	
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
	infile = open('teste_beta3.bin', 'rb')

	sliding_window = array.array('c')
	data_buffer = array.array('c')
	header_buffer = array.array('c')
	buffer_1 = array.array('c') # Buffer de pesquisa				aka "from RAM"
	buffer_2 = array.array('c') # Buffer de dados sem ocorrência	aka "from ROM"

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

	print '... Uma tool Monkeys Traducoes ...'
	print 'Copyright Hansen - 2010'
	
	opt = int(raw_input('\n[1] Extrair Imagens \n[2] Inserir Imagens (Teste) \n[3] Sair \n'))
	
	if opt == 1:
		extract()
		sys.exit(1)
	elif opt == 2:
		insert()
		sys.exit(1)
	elif opt == 3:
		sys.exit(1)

