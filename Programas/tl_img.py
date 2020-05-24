#!/usr/bin/env python
# -*- coding: windows-1252 -*-
'''
Created on 13/06/2013

@author: diego.hahn
'''

import re
import struct
import array
import os
import glob
import sys
import shutil
import tempfile

from rhCompression import lzss, rle, huffman
from rhImages import images, bmp

__title__ = "Layton's Image Processor"
__version__ = "2.0"

PATH = r'../ROM Original/Splitted/LAYTON2/data_lt2'

UNPACK_INPUT_PATH = r'../Imagens Originais'
PACK_OUTPUT_PATH = r'../Arquivos Gerados'    

def gba2tuple(fd):
    rgb = struct.unpack('<H', fd.read(2))[0] & 0x7FFF
    rgb = map(lambda x,y: float((x >> y) & 0x1F)/31.0, [rgb]*3, [0,5,10])
    return rgb
    
def tuple2gba(color):
    r, g, b = map(lambda x: int(float(x)/255.0*31), color)
    color = ((b << 10) | (g << 5) | r ) & 0x7FFF
    return struct.pack('<H', color)

def scandirs(path):
    files = []
    for currentFile in glob.glob( os.path.join(path, '*') ):
        if os.path.isdir(currentFile):
            files += scandirs(currentFile)
        else:
            files.append(currentFile)
    return files

def unpackBackground( src, dst ):
    bg_path = os.path.join(src, 'bg')
    files = filter(lambda x: x.__contains__('.arc'), scandirs(bg_path))
        
    for _, fname in enumerate(files):
        print fname
        
        path = fname[len(src):]
        fdirs = dst + path[:-len(os.path.basename(path))]
        if not os.path.isdir(fdirs):
            os.makedirs(fdirs)          
        
        temp = open('temp', 'w+b')  
        file = open(fname, 'rb')
        type = struct.unpack('<L', file.read(4))[0]
        if type == 1:
            buffer = rle.uncompress(file, 0x4)
        elif type == 2:     
            buffer = lzss.uncompress(file, 0x4)
        elif type == 3 or type == 4:
            buffer = huffman.uncompress(file, 0x4)
        else:
            file.seek(0,0)
            buffer = array.array('c', file.read())
        buffer.tofile(temp)
        file.close()
        
        temp.seek(0,0)
        # L? a paleta de cores
        colormap = []
        entries = struct.unpack('<L', temp.read(4))[0]
        for _ in range(entries):
            colormap.append(gba2tuple(temp))
        
        # L? o tile set da imagem
        tilelist = []   
        ntiles = struct.unpack('<L', temp.read(4))[0]
        for _ in range(ntiles):
            tilelist.append(temp.read(64))
            
        # L? os par?metros da imagem e o tilemap
        buffer = array.array('c')
        width = struct.unpack('<H', temp.read(2))[0]
        height = struct.unpack('<H', temp.read(2))[0]
        for x in range(width*height):
            bytes = struct.unpack('<H', temp.read(2))[0]
            # v_mirror = bytes & 0x0800
            # h_mirror = bytes & 0x0400
            string = tilelist[bytes & 0x3FF]
            # if v_mirror:
                # string = vertical(string)
            # if h_mirror:
                # string = horizontal(string)
            buffer.extend(string)
                   
        output = open(fdirs + os.path.basename(path) + '.bmp', 'wb')

        w = images.Writer((width << 3, height << 3), colormap, 8, 1, 0)
        w.write(output, buffer, 8, 'BMP')
        
        output.close()
        temp.close()
            
    os.unlink(temp.name)
    
    
def packBackground( src, dst ):
    outdir = ['../Imagens/bg_pt/', '../Imagens/bg_pt/pt/']
    originals = ['../Imagens/bg/', '../Imagens/bg/en/']
    
    bg_path = os.path.join(src, 'bg')
    files = filter(lambda x: x.__contains__('.bmp'), scandirs(bg_path))    
    
    print "Buffering..."

    for name in files:    
    
    # for i, dir in enumerate(['../Imagens/_bg_pt/', '../Imagens/_bg_pt/pt/']):
        # for name in os.listdir(dir):
            # if name in ('es', 'en', 'de', 'it', 'fr', 'pt'): pass
            # else:
                # print name
                
                input = open(name, 'rb')
                w = images.Reader(input)
                data, colormap = w.as_data(mode = 1, bitdepth = 8)

                width = len(w.data[0])
                height = len(w.data)
                
                tilelist = []
                tileset = array.array('c')
                tilemap = array.array('c')
                
                for x in range(width*height/64):
                    string = data[64*x:64*(x+1)]
                    if string in tilelist:
                        mapper = tilelist.index(string)
                        tilemap.extend(struct.pack('<H', mapper))
                    else:
                        tilelist.append(string)
                        mapper = tilelist.index(string)
                        tileset.extend(string)
                        tilemap.extend(struct.pack('<H', mapper))
                    
                temp = open('temp', 'w+b')
                # Escrita do arquivo tempor?rio:
                temp.write(struct.pack('<L', 0xE0))#len(colormap)))
                for x in range(0xE0):#colormap:
                    temp.write(tuple2gba(colormap[x]))
                temp.write(struct.pack('<L', len(tilelist)))
                tileset.tofile(temp)
                
                temp.write(struct.pack('<H', width / 8))
                temp.write(struct.pack('<H', height / 8))
                tilemap.tofile(temp)
                
                filepath = dst + name[len(src):]
                path  = os.path.dirname( filepath )
                if not os.path.isdir( path ):
                    os.makedirs( path )                   
                
                output = open(filepath.replace('.bmp', ''), 'wb')
                output.write(struct.pack('<L', 2))
                
                buffer = lzss.compress(temp)             
                buffer.tofile(output)
                
                output.close()
                temp.close()
                
                print '>> \'' + filepath.replace('.bmp', '') + ' created.'
                
def unpackSprite( src, dst ):
    ani_path = os.path.join(src, 'ani')
    files = filter(lambda x: x.__contains__('.arc') or x.__contains__('.arj'), scandirs(ani_path))
        
    for _, name in enumerate(files):
    
        path = name[len(src):]
        fname = os.path.basename(path)
        fdirs = dst + path[:-len(fname)]
        if not os.path.isdir(fdirs):
            os.makedirs(fdirs)              

        with open('temp', 'w+b') as f:
            if name in ('es', 'en', 'de', 'it', 'fr'):
                pass
            else:
                print name

                file = open(name, 'rb')
                type = struct.unpack('<L', file.read(4))[0]
                if type == 1:
                    buffer = rle.uncompress(file, 0x4)
                elif type == 2:     
                    buffer = lzss.uncompress(file, 0x4)
                elif type == 3 or type == 4:
                    buffer = huffman.uncompress(file, 0x4)
                else:
                    file.seek(0,0)
                    buffer = array.array('c', file.read())
                buffer.tofile(f)
                file.close()

                if re.match(r'^.*\.arc$', name):
                    f.seek(0,0)
                    entries = struct.unpack('<H', f.read(2))[0]
                    type = struct.unpack('<H', f.read(2))[0]
                    objs = []
                    
                    if type == 3:
                        for p in range(entries):
                            xcoord = struct.unpack('<H', f.read(2))[0]
                            ycoord = struct.unpack('<H', f.read(2))[0]
                            obj_entries = struct.unpack('<L', f.read(4))[0]
                            
                            objs_params = []
                            
                            for x in range(obj_entries):
                                obj_xcoord = struct.unpack('<H', f.read(2))[0]
                                obj_ycoord = struct.unpack('<H', f.read(2))[0]          
                                obj_width = 4 * (2 ** struct.unpack('<H', f.read(2))[0]) # 4 BPP)
                                obj_height = 8 * (2 ** struct.unpack('<H', f.read(2))[0])
                                obj_data = []

                                for y in range(obj_height):
                                    obj_data.append(f.read(obj_width))
                                    
                                objs_params.append( (obj_xcoord, obj_ycoord,
                                                     obj_width, obj_height, obj_data) )

                            width = 0
                            height = 0

                            for obj_param in objs_params:
                                if width <= obj_param[0] + obj_param[2]*2:
                                    width = obj_param[0] + obj_param[2]*2
                                if height <= obj_param[1] + obj_param[3]:
                                    height = obj_param[1] + obj_param[3]

                            buffer = array.array('c', '\xFF' * width * height)

                            for obj_param in objs_params:
                                obj_data = obj_param[4]
                                for y in range(obj_param[3]):
                                    buffer[width/2*(obj_param[1] + y) + (obj_param[0])/2:
                                           width/2*(obj_param[1] + y) + (obj_param[0])/2 + obj_param[2]] = array.array('c', obj_data.pop(0))                        

                            objs.append((width, height, buffer))
                                           
                        pal_entries = struct.unpack('<L', f.read(4))[0]         
                        colormap = []
                        for x in range(pal_entries):
                            colormap.append(gba2tuple(f))

                        for x in range(entries):                             
                            output = open(os.path.join(fdirs, '%s-%02d-%02d.bmp' %(fname, (x+1), entries)), 'wb')
                            w = images.Writer((objs[x][0], objs[x][1]), colormap, 4, 2)
                            w.write(output, objs[x][2], 4, 'BMP')
                            output.close()

                    elif type == 4:
                        for p in range(entries):
                            xcoord = struct.unpack('<H', f.read(2))[0]
                            ycoord = struct.unpack('<H', f.read(2))[0]
                            obj_entries = struct.unpack('<L', f.read(4))[0]
                            
                            objs_params = []                        

                            for x in range(obj_entries):
                                obj_xcoord = struct.unpack('<H', f.read(2))[0]
                                obj_ycoord = struct.unpack('<H', f.read(2))[0]          
                                obj_width = 8 * (2 ** struct.unpack('<H', f.read(2))[0])
                                obj_height = 8 * (2 ** struct.unpack('<H', f.read(2))[0])
                                obj_data = []
                                for y in range(obj_height):
                                    obj_data.append(f.read(obj_width))                          

                                objs_params.append( (obj_xcoord, obj_ycoord,
                                                     obj_width, obj_height, obj_data) )
                    
                            width = 0
                            height = 0

                            for obj_param in objs_params:
                                if width <= obj_param[0] + obj_param[2]:
                                    width = obj_param[0] + obj_param[2]
                                if height <= obj_param[1] + obj_param[3]:
                                    height = obj_param[1] + obj_param[3]                        

                            buffer = array.array('c', '\xFF' * width * height)
                            
                            for obj_param in objs_params:
                                obj_data = obj_param[4]
                                for y in range(obj_param[3]):
                                    buffer[width*(obj_param[1] + y) + (obj_param[0]):
                                           width*(obj_param[1] + y) + (obj_param[0]) + obj_param[2]] = array.array('c', obj_data.pop(0))                        
                    
                            objs.append((width, height, buffer))

                        pal_entries = struct.unpack('<L', f.read(4))[0]         
                        colormap = []
                        for x in range(pal_entries):
                            colormap.append(gba2tuple(f))                               
                            
                        for x in range(entries):
                            output = open(os.path.join(fdirs, '%s-%02d-%02d.bmp' %(fname, (x+1), entries)), 'wb')
                            w = images.Writer((objs[x][0], objs[x][1]), colormap, 8, 2)
                            w.write(output, objs[x][2], 8, 'BMP')
                            output.close()                                                  
                        
                    else:
                        print 'except %s' % name

                elif re.match(r'^.*\.arj$', name):
                    f.seek(0,0)
                    objs = []
                
                    entries = struct.unpack('<H', f.read(2))[0]
                    type = struct.unpack('<H', f.read(2))[0]                        
                    pal_entries = struct.unpack('<L', f.read(4))[0]
                    for p in range(entries):
                        xcoord = struct.unpack('<H', f.read(2))[0]
                        ycoord = struct.unpack('<H', f.read(2))[0]
                        obj_entries = struct.unpack('<L', f.read(4))[0]
                        
                        objs_params = []
                        
                        for x in range(obj_entries):
                            obj_shape = struct.unpack('<H', f.read(2))[0]
                            obj_size = struct.unpack('<H', f.read(2))[0]
                            obj_xcoord = struct.unpack('<H', f.read(2))[0]
                            obj_ycoord = struct.unpack('<H', f.read(2))[0]
                            obj_width = 8 * (2**struct.unpack('<H', f.read(2))[0])
                            obj_height = 8 * (2**struct.unpack('<H', f.read(2))[0]) 
                            obj_data = []
                            for y in range(obj_width * obj_height / 64):
                                obj_data.append(f.read(64))
                                
                            objs_params.append( (obj_shape, obj_size, obj_xcoord, obj_ycoord,
                                                 obj_width, obj_height, obj_data) )
                        width = 0
                        height = 0

                        for obj_param in objs_params:
                            if width <= obj_param[2] + obj_param[4]:
                                width = obj_param[2] + obj_param[4]
                            if height <= obj_param[3] + obj_param[5]:
                                height = obj_param[3] + obj_param[5]
                                                                    
                        buffer = array.array('c', '\xFF' * width * height)
                        
                        for obj_param in objs_params:
                            obj_data = obj_param[6]
                            for y in range(obj_param[5] / 8):
                                for w in range(obj_param[4] / 8):
                                    buffer[(width*(obj_param[3] + y*8)) + obj_param[2]*8 + 64*(w):
                                           (width*(obj_param[3] + y*8)) + obj_param[2]*8 + 64*(w+1)] = array.array('c',obj_data.pop(0))

                        objs.append((width, height, buffer))
                
                    colormap = []
                    for _ in range(pal_entries):
                        colormap.append(gba2tuple(f))

                    for x in range(entries):
                        output = open(os.path.join(fdirs, '%s-%02d-%02d.bmp' %(fname, (x+1), entries)), 'wb')
                        w = images.Writer((objs[x][0], objs[x][1]), colormap, 8, 1)
                        w.write(output, objs[x][2], 8, 'BMP')
                        output.close()
                            
def packSprite( src, dst, src1 ):
    holder = {}

    # Passo 1 - Gerar um dicion?rio com todos os sprites a serem empacotados
    
    ani_path = os.path.join(src, 'ani')
    files = filter(lambda x: x.__contains__('.bmp'), scandirs(ani_path))    
    
    print "Buffering..."

    for name in files:
        print ">>> ", name
        a = re.match( r'(.*)-(.*)-(.*)\.bmp$', name[len(src):] )
        if a.group(1) not in holder:
            holder.update({a.group(1):{}})#[]})
            
        w = bmp.Reader( name )
        d = w.read()
        p = w.read_palette()
        w.file.close()
        holder[a.group(1)].update({int(a.group(2)) - 1: (d,p)})#append((d, p))
        
    print "Analyzing..."       
        
    compressions = {}
    data = {}
    # Passo 2 - Descompactar os arquivos originais
    for name in holder.keys():  
        file = open( src1 + name , "rb")
        type = struct.unpack('<L', file.read(4))[0]
        if type == 1:
            buffer = rle.uncompress(file, 0x4)
        elif type == 2:     
            buffer = lzss.uncompress(file, 0x4)
        elif type == 3 or type == 4:
            buffer = huffman.uncompress(file, 0x4)
        else:
            file.seek(0,0)
            buffer = array.array('c', file.read())
        compressions.update({name:type})
        file.close()

        data.update( {name:buffer} )
                
    # Passo 3 - Atualizar os containers com os novos sprites
    #for i, dir in enumerate(outdir):
    for name in data.keys():
        print "Updating ", name
        buffer = data[name]
        arrays = []
        with open( "temp", "w+b") as f:
            buffer.tofile( f )            
            f.seek(0,0)
            if re.match(r'^.*\.arc$', name):
                entries = struct.unpack("<H", f.read(2))[0]
                bitdepth = 2 ** (struct.unpack("<H", f.read(2))[0] - 1)
                for x in range(entries):
                    sprite_data = holder[name][x][0]
                    sprite_pal = holder[name][x][1]
                    # Leitura do header do sprite
                    f.seek(4, 1) # As coordenadas n?o ser?o mudadas a principio
                    obj_entries = struct.unpack("<L", f.read(4))[0]
                    for y in range(obj_entries):
                        xpos = struct.unpack("<H", f.read(2))[0]
                        ypos = struct.unpack("<H", f.read(2))[0]
                        width = 8 * (2 ** struct.unpack("<H", f.read(2))[0])
                        height = 8 * (2 ** struct.unpack("<H", f.read(2))[0])
                        obj = []
                        for w in range(height):
                            obj.append(sprite_data[ypos + w][xpos:xpos + width])

                        bitarray = array.array('B')
                        for row in obj:
                            if bitdepth < 8:
                                row = zip(*[iter(row)]*(8/bitdepth))
                                row = map(lambda e: reduce(lambda x,y:(x << bitdepth) + y, reversed(e)), row)
                            bitarray.extend(row)
                            
                        arrays.append((f.tell(), array.array("c", bitarray.tostring())))
                        f.seek(len(bitarray.tostring()), 1)

                pal_entries = struct.unpack('<L', f.read(4))[0]
                
            elif re.match(r'^.*\.arj$', name): 
                entries = struct.unpack("<H", f.read(2))[0]
                bitdepth = 2 ** (struct.unpack("<H", f.read(2))[0] - 1)
                colors = struct.unpack("<L", f.read(4))[0]
                for x in range(entries):
                    sprite_data = holder[name][x][0]
                    sprite_pal = holder[name][x][1]
                    
                    sprite_xpos = struct.unpack("<H", f.read(2))[0]
                    sprite_ypos = struct.unpack("<H", f.read(2))[0]
                    obj_entries = struct.unpack("<L", f.read(4))[0]
                    
                    for y in range(obj_entries):
                        obj_shape = struct.unpack('<H', f.read(2))[0]
                        obj_size = struct.unpack('<H', f.read(2))[0]
                        obj_xcoord = struct.unpack('<H', f.read(2))[0]
                        obj_ycoord = struct.unpack('<H', f.read(2))[0]
                        obj_width = 2**struct.unpack('<H', f.read(2))[0]
                        obj_height = 2**struct.unpack('<H', f.read(2))[0]
                        
                        obj = [[list() for p in range(obj_width)] for t in range(obj_height)]

                        for ypos in range(obj_height):
                            for xpos in range(obj_width):
                                for w in range(8):
                                    obj[ypos][xpos] += (sprite_data[obj_ycoord + ypos*8 + w][obj_xcoord + xpos*8:obj_xcoord + xpos*8 + 8])
                            
                        bitarray = array.array('B')
                        for row in obj:
                            for d in row:
                                bitarray.extend(d)
                            
                        arrays.append((f.tell(), array.array("c", bitarray.tostring())))
                        f.seek(len(bitarray.tostring()), 1)
                        
        with open( "temp", "r+b") as f: 
            for par in arrays:
                f.seek(par[0], 0)
                par[1].tofile(f)                

                
# Passo 4
        print "Compressing..."

        with open( "temp", "rb") as f:
            type = compressions[name]
            if type == 1:
                buffer = rle.compress(f)
            elif type == 2:
                buffer = lzss.compress(f)
            elif type == 3:
                buffer = huffman.compress(f, 4)
            elif type == 4:
                buffer = huffman.compress(f, 8)

            filepath = dst + name
            path  = os.path.dirname( filepath )
            #print path
            if not os.path.isdir( path ):
                os.makedirs( path )               
                
            g = open( filepath, "wb")
            g.write(struct.pack("<L", type))
            buffer.tofile(g)
            g.close()
            
            print '>> \'' + filepath + ' created.'            
                            
if __name__ == "__main__":

    import argparse
    
    os.chdir( sys.path[0] )
    #os.system( 'cls' )

    print "{0:{fill}{align}70}".format( " {0} {1} ".format( __title__, __version__ ) , align = "^" , fill = "=" )

    parser = argparse.ArgumentParser()
    parser.add_argument( '-m', dest = "mode", type = str, required = True )
    parser.add_argument( '-s', dest = "src", type = str, nargs = "?", required = True )
    parser.add_argument( '-s1', dest = "src1", type = str, nargs = "?" )
    parser.add_argument( '-d', dest = "dst", type = str, nargs = "?", required = True )
    
    args = parser.parse_args()
    
    # dump bg
    if args.mode == "e0":
        print "Unpacking background"
        unpackBackground( args.src , args.dst )
    # insert bg
    elif args.mode == "i0": 
        print "Packing background"
        packBackground( args.src , args.dst )
    # dump ani
    elif args.mode == "e1": 
        print "Unpacking animation"
        unpackSprite( args.src , args.dst )
    # insert ani
    elif args.mode == "i1": 
        print "Packing animation"
        print args.src1
        packSprite( args.src , args.dst , args.src1 )
    else:
        sys.exit(1)
