#!/usr/bin/env python
# -*- coding: utf-8 -*-

# images/palette.py

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
	Módulo para gerenciamento de paletas.
'''

from __future__ import division

__author__ = "Diego Hansen Hahn"
__version__ = "v2.0.2"

import struct

import gtk
import gobject

POSITION = 0x18

# Funções de conversão de cores
def tuple2rgb(r, g, b):
	rgb = (int(r * 0xF8) << 16 | int(g * 0xF8) << 8 | int(b * 0xF8)) & 0xFFFFFF
	return struct.pack('<L', rgb)

def rgb2tuple(fd):
	try:
		rgb = struct.unpack('<L', fd.read(4))[0] & 0xFFFFFF # Filtra o canal alfa
		rgb = map(lambda x,y: float((x >> y) & 0xF8)/248.0, [rgb]*3, [0,8,16])
		return rgb
	except:
		return (0,0,0)

def tuple2gba(r, g, b):
	rgb = ((int(b * 31) << 10) | (int(g * 31) << 5) | int(r * 31) ) & 0x7FFF
	return struct.pack('<H', rgb)

def gba2tuple(fd):
	try:
		rgb = struct.unpack('<H', fd.read(2))[0] & 0x7FFF
		rgb = map(lambda x,y: float((x >> y) & 0x1F)/31.0, [rgb]*3, [0,5,10])
		return rgb
	except:
		return (0,0,0)

class Palette:
	@property
	def codec_1bpp(self):
		return 1
	@property
	def codec_2bpp(self):
		return 2
	@property
	def codec_4bpp(self):
		return 4
	@property
	def codec_8bpp(self):
		return 8

	@property
	def colors_gray(self):
		return 0
	@property
	def colors_romfile(self):
		return 1
	@property
	def colors_buffer(self):
		return 2
	@property
	def colors_extern(self):
		return 3

	colors_list = [list(), list(), list(), list()]
	colors = None

	def __init__(self, file = None):

		self.set_codec(self.codec_4bpp)

		self.set_palette_number(0)
		self.set_palette_mode(self.colors_gray)
		self.generate_grayscale_pal()

# Funções Auxiliares
# ---------------------------------------------------------------------------------------------------------
	def set_codec(self, codec):
		if codec in (self.codec_1bpp, self.codec_2bpp, self.codec_4bpp, self.codec_8bpp):
			self.codec = codec
			self.generate_grayscale_pal()

	def get_codec(self):
		return self.codec

	def is_codec(self, codec):
		return self.codec == codec

	def set_palette_mode(self, mode):
		if mode in (self.colors_gray, self.colors_extern, self.colors_buffer, self.colors_romfile):
			self.mode = mode
			self.colors = self.colors_list[mode]

	def get_palette_mode(self):
		return self.mode

	def is_palette_mode(self, mode):
		return self.mode == mode

	def set_palette_number(self, number):
		self.palette_number = number

	def __getitem__(self, key):
		return self.colors[key]

	def __iter__(self):
		for k in [x for x in range(256)
				  if (x >= self.palette_number*2**self.codec) and (x < self.palette_number*2**self.codec+2**self.codec)]:
			yield self.colors[k]

	def __len__(self):
		return len(self.colors)

# Preenchimento das Paletas
# ---------------------------------------------------------------------------------------------------------
	def generate_pal_from_extern(self, file):
		self.colors_list[self.colors_extern] = list()
		if file.name.split('.')[1].lower() == 'pal':
			file.seek(POSITION, 0)
			for x in range(256):
				alpha = 0 if x == 0 else 1
				rgb = rgb2tuple(file)
				self.colors_list[self.colors_extern].append((rgb[0], rgb[1], rgb[2], alpha))
		else:
			file.seek(0, 0)
			for x in range(256):
				alpha = 0 if x == 0 else 1
				rgb = gba2tuple(file)
				self.colors_list[self.colors_extern].append((rgb[0], rgb[1], rgb[2], alpha))

	def generate_pal_from_rom(self, file, address):
		self.colors_list[self.colors_romfile] = list()
		file.seek(address, 0)
		for x in range(256):
			alpha = 0 if x == 0 else 1
			rgb = gba2tuple(file)
			self.colors_list[self.colors_romfile].append((rgb[0], rgb[1], rgb[2], alpha))

	def generate_grayscale_pal(self):
		self.colors_list[self.colors_gray] = list()
		colors = 2**self.codec
		for x in range(256):
			alpha = 0 if x == 0 else 1
			c = (x % colors) / (colors - 1)
			self.colors_list[self.colors_gray].append((c, c, c, alpha))

	def generate_buffer_pal(self, buffer, address):
		import mmap

		self.colors_list[self.colors_buffer] = list()
		map = mmap.mmap(-1, len(buffer))
		map[:] = buffer.tostring()
		if address > len(map):
			address = len(map)
		map.seek(address, 0)
		for x in range(256):
			alpha = 0 if x == 0 else 1
			rgb = gba2tuple(map)
			self.colors_list[self.colors_buffer].append((rgb[0], rgb[1], rgb[2], alpha))
		map.close()

		del mmap

	def change_color(self, rgb, index):
		self.colors[(index - 1)] = rgb

# Funções I/O
# ---------------------------------------------------------------------------------------------------------
	def tofile(self, file, colormap):
		# Palette-header chunk
		file.write('RIFF')	  # Identificador
		file.write(struct.pack('<L', 16 + 2**(self.codec))) # Tamanho do arquivo (menos o identificador e este chunk)
		file.write('PAL ')	  # Identificador subchunk
		file.write('data')	  # Início struct LOGPALETTE
		file.write(struct.pack('<L', 4 + 2**(self.codec))) # Tamanho struct LOGPALETTE
		# LOGPALETTE
		file.write(struct.pack('<H', 768))  # palVersion - Versão Windows 3.0
		file.write(struct.pack('<H', 2**(self.codec)))  # palEntries - Quantidade de entradas

		for color in colormap:
			file.write(tuple2rgb(color[2], color[1], color[0]))

		return True

	def fromfile(self, file):
		colormap = []

		file.seek(0x16, 0)
		entries = struct.unpack('<H', file.read(2))[0]
		for x in range(entries):
			colormap.append(rgb2tuple(file))

		return colormap



LEFT_BUTTON = 1
RIGHT_BUTTON = 3

class PaletteWidget(gtk.DrawingArea):

	__gsignals__ = {'realize' : 'override',
					'expose-event' : 'override',
					'button-press-event' : 'override',
					'motion-notify-event' : 'override',
					'one-click': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
					'double-click': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
					'colors-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())}

	def __init__(self):
		gtk.DrawingArea.__init__(self)

		self.add_events(gtk.gdk.BUTTON_MOTION_MASK | gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK)

		self.colors = []
		# Inicia as cores em uso
		self.over_color = None
		self.previous_color = None

		self.first_color = None
		self.second_color = None
		# Os eventos não podem coexistir!!
		self.button_event_one = False
		self.button_event_two = False

	def set_button_event_one(self, event):
		self.button_event_one = event
		# Se ligar o evento do botão esquerdo, desliga o do direito
		if event:
			self.button_event_two = False

	def set_button_event_two(self, event):
		self.button_event_two = event
		# Se ligar o evento do botão direito, desliga o do esquerdo
		if event:
			self.button_event_one = False

	def add_color(self, color):
		self.colors.append(color)

	def clear_colors(self):
		self.colors = []

	def do_realize(self):
		self.set_flags(self.flags() | gtk.REALIZED)

		events = gtk.gdk.EXPOSURE_MASK | gtk.gdk.BUTTON_PRESS_MASK | \
				 gtk.gdk.POINTER_MOTION_MASK

		self.window = gtk.gdk.Window(self.get_parent_window(),
									 x=self.allocation.x,
									 y=self.allocation.y,
									 width=self.allocation.width,
									 height=self.allocation.height,
									 window_type=gtk.gdk.WINDOW_CHILD,
									 wclass=gtk.gdk.INPUT_OUTPUT,
									 visual=self.get_visual(),
									 colormap=self.get_colormap(),
									 event_mask=self.get_events() | events)

		self.window.set_user_data(self)
		self.style.attach(self.window)
		self.style.set_background(self.window, gtk.STATE_NORMAL)

	def do_expose_event(self, event):
		self.context = self.window.cairo_create()
		self.context.rectangle(event.area.x, event.area.y,
						  event.area.width, event.area.height)
		self.context.clip()

		# Desenha as cores
		for color in self.colors:
			color.draw(self.context)

		# Desenha a grade:
		self.context.set_source_rgb(0.5, 0.5, 0.5)
		self.context.set_line_width(0.1)
		for x in range(1, 162, 10):
			self.context.move_to(x, 0)
			self.context.line_to(x, 162)
			self.context.move_to(0, x)
			self.context.line_to(162, x)
		self.context.stroke()

		# Desenha a seleção
		for color in self.colors:
			color.draw_selection(self.context)

		return False

	def do_button_press_event(self, event):
		# Evento Um:
		# Um clique: seleciona a coir
		# Dois cliques: emite sinal de clique duplo
		if event.button == LEFT_BUTTON and self.button_event_one:
			if event.type == gtk.gdk.BUTTON_PRESS:
				if self.over_color:
					if self.previous_color:
						self.previous_color.unpress()
					self.previous_color = self.over_color
					self.over_color.press()
					self.refresh()
					self.emit('one-click')
			elif event.type == gtk.gdk._2BUTTON_PRESS:
				if self.over_color:
					self.emit('double-click')
		# Evento Dois:
		# Um clique: Seleciona uma cor
		# Outro clique: Troca de lugar as cores
		elif event.button == LEFT_BUTTON and self.button_event_two:
			if event.type == gtk.gdk.BUTTON_PRESS:
				if self.over_color:
					self.over_color.press()
					if self.first_color:
						self.second_color = self.over_color
					else:
						self.first_color = self.over_color

			if self.first_color and self.second_color:
				# Troca as cores
				self.second_color.rgb_value, self.first_color.rgb_value = self.first_color.rgb_value, self.second_color.rgb_value
				self.first_color.unpress()
				self.second_color.unpress()
				self.first_color = None
				self.second_color = None

				# Emite sinal de troca de lugar das cores
				self.emit('colors-changed')

			self.refresh()

		return False

	def do_motion_notify_event(self, event):
		pos = (event.x, event.y)
		for color in self.colors:
			if color.is_mouse_over(pos):
				self.over_color = color
				return False
		self.over_color = None

	def refresh(self):
		alloc = self.get_allocation()
		rect = gtk.gdk.Rectangle(0, 0, alloc.width, alloc.height)
		self.window.invalidate_rect(rect, True)
		self.window.process_updates(True)

	def __iter__(self):
		for color in self.colors:
			yield color

class Colors(gobject.GObject):

	HEIGHT = 10
	WIDTH = 10

	def __init__(self, id, rgba, pos):
		gobject.GObject.__init__(self)

		setattr(self, 'id', id)

		self.pos = pos
		self.rgb_value = (rgba[0],rgba[1],rgba[2])

		self.pressed = False

	def draw(self, context):
		context.set_source_rgb(*self.rgb_value)
		context.rectangle(self.pos[0], self.pos[1], Colors.WIDTH, Colors.HEIGHT)
		context.fill()

	def draw_selection(self, context):
		if not self.pressed:
			return
		context.set_line_width(2)
		context.set_source_rgb(1, 0, 0)
		context.rectangle(self.pos[0], self.pos[1], Colors.WIDTH, Colors.HEIGHT)
		context.stroke()

	def is_mouse_over(self, pos):
		if (pos[0] > self.pos[0] and pos[0] < (self.pos[0] + Colors.HEIGHT )) and \
		   (pos[1] > self.pos[1] and pos[1] < (self.pos[1] + Colors.WIDTH )):
			return True
		return False

	def press(self):
		self.pressed = True

	def unpress(self):
		self.pressed = False

	def set_color(self, rgba):
		self.rgb_value = (rgba[0],rgba[1],rgba[2])

	def get_color(self):
		return self.rgb_value
