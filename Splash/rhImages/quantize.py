#!/usr/bin/env python
# -*- coding: utf-8 -*-

# images/quantize.py

# Copyright 2009-2010 Diego Hansen Hahn (aka DiegoHH) <diegohh90 [at] hotmail [dot] com>

# Copyright 2000 Adam Doppelt (Java Version)
# Copyright 1992 John Cristy (Original Code - from ImageMagick)

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
    Módulo para redução de cores de imagens.
    Eficiente para arquivos pequenos (até 256x256) (3~4 segundos)

    Para entendimento do algoritmo aplicado (quantização de cores por octrees):
    - http://www.cubic.org/docs/octree.htm

    Código baseado na versão Java feita por Adam Doppelt:
    - http://gurge.com/amd/java/quantize/index.html
'''

__author__ = "Diego Hansen Hahn"
__version__ = "v2.0.2"

MAX_RGB = 255
MAX_NODES = 266817
MAX_TREE_DEPTH = 8

SHIFT = [(1 << (15 - (i+1))) for i in range(MAX_TREE_DEPTH+1)]

# Consigo deixar mais rápido????

class OctreeNode:
    def __init__(self, cube = None, parent = None, id = None, level = None):
        self.child = [None, None, None, None, None, None, None, None]
        self.nchild = 0
        self.unique = 0
        self.total_red = 0
        self.total_green = 0
        self.total_blue = 0
        self.color_number = 0

        self.id = id
        self.level = level
        self.number_pixels = 2147483647

        if isinstance(cube, Cube):
            self.cube = cube
            self.parent = self

            self.mid_red = (MAX_RGB + 1) >> 1
            self.mid_green = (MAX_RGB + 1) >> 1
            self.mid_blue = (MAX_RGB + 1) >> 1

        else:
            self.cube = parent.cube
            self.number_pixels = 0
            self.parent = parent

            self.cube.nodes += 1

            if (level == self.cube.depth):
                self.cube.colors += 1

            self.parent.nchild += 1
            self.parent.child[id] = self

            bi = (1 << (MAX_TREE_DEPTH - level)) >> 1
            self.mid_red = parent.mid_red + (bi if ((id & 1) > 0) else -bi)
            self.mid_green = parent.mid_green + (bi if ((id & 2) > 0) else -bi)
            self.mid_blue = parent.mid_blue + (bi if ((id & 4) > 0) else -bi)

    def pruneChild(self):
        '''
        Remove o nó filho e transmite as estatísticas dos pixel
        para o nó pai
        '''
        self.parent.nchild -= 1
        self.parent.unique += self.unique
        self.parent.total_red += self.total_red
        self.parent.total_green += self.total_green
        self.parent.total_blue += self.total_blue
        self.parent.child[self.id] = None
        self.cube.nodes -= 1
        self.cube = None
        self.parent = None

    def pruneLevel(self):
        '''
        Remove os ramos mais afastados da árvore
        '''
        if self.nchild != 0:
            for id in range(8):
                if self.child[id] != None:
                    self.child[id].pruneLevel()
        if self.level == self.cube.depth:
            self.pruneChild()

    def reduce(self, threshold, next_threshold):
        if self.nchild != 0:
            for id in range(8):
                if self.child[id]:
                    next_threshold = self.child[id].reduce(threshold,next_threshold)
        if self.number_pixels <= threshold:
            self.pruneChild()
        else:
            if self.unique != 0:
                self.cube.colors += 1
            if self.number_pixels < next_threshold:
                next_threshold = self.number_pixels
        return next_threshold

    def colormap(self):
        '''
        Varre a árvore montando o mapa de cores.
        '''
        if self.nchild != 0:
            for id in range(8):
                if self.child[id]:
                    self.child[id].colormap()
        if self.unique != 0:
            red = ((self.total_red + (self.unique >> 1)) / self.unique)
            green = ((self.total_green + (self.unique >> 1)) / self.unique)
            blue = ((self.total_blue + (self.unique >> 1)) / self.unique)
            self.cube.colormap[self.cube.colors] = (red, green, blue)
            self.color_number = self.cube.colors
            self.cube.colors += 1

class Cube:
    def __init__(self, pixels, max_colors):
        self.pixels = pixels
        self.max_colors = max_colors
        self.colors = 0
        self.nodes = 0
        self.depth = 1
        self.colormap = []
        i = max_colors

        self.depth = MAX_TREE_DEPTH

        self.root = OctreeNode(cube = self, id = 0, level = 0)

    def classification(self):
        pixels = self.pixels
        for row in pixels:
            for pixel in row:
                red = pixel[0]
                green = pixel[1]
                blue = pixel[2]

                if self.nodes > MAX_NODES:
                    self.root.pruneLevel()
                    self.depth -= 1

                node = self.root
                for level in range(1,9):
                    id = (((1 if (red > node.mid_red) else 0)) |
                          ((1 if (green > node.mid_green) else 0) << 1) |
                          ((1 if (blue > node.mid_blue) else 0) << 2))
                    if not node.child[id]:
                        OctreeNode(parent = node, id = id, level = (level))
                    node = node.child[id]
                    node.number_pixels += SHIFT[(level)]
                node.unique += 1
                node.total_red += red
                node.total_green += green
                node.total_blue += blue
        return

    def reduction(self):
        threshold = 1
        while self.colors > self.max_colors:
            self.colors = 0
            threshold = self.root.reduce(threshold, 2147483647)
        return

    def assignment(self):
        self.colormap = [(0,0,0)] * self.max_colors
        self.colors = 0

        self.root.colormap()

        pixels = self.pixels
        self.image = []
        for row in pixels:
            new_row = []
            for pixel in row:
                red = pixel[0]
                green = pixel[1]
                blue = pixel[2]

                node = self.root
                while True:
                    id = (((1 if (red > node.mid_red) else 0) << 0) |
                          ((1 if (green > node.mid_green) else 0) << 1) |
                          ((1 if (blue > node.mid_blue) else 0) << 2))
                    if not node.child[id]:
                        break
                    node = node.child[id]
                new_row.append(node.color_number)
            self.image.append(new_row)
