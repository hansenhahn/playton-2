#!/usr/bin/env python
# -*- coding: windows-1252 -*-
'''
Created on 01/08/2013

@author: Hansen
'''
import time
import re
import glob
import os.path
import struct
import array
import sys
import mmap

from rhCompression import lzss
from pytable import normal_table

DEBUG = 0

FULL_PATH = '../ROM Original/Splitted/LAYTON2/data_lt2'
# FULL_PATH = r"C:\Users\Hansen\Romhacking\Projetos\[NDS] Professor Layton and Pandora's Box\ROM Original\Splitted\LAYTON2\data_lt2"

#FOLDERS = ["place/en", "txt/en"]
FOLDERS = ["nazo/en"]
#FOLDERS = ["txt/en"]

OUTPATH = "../Textos Originais"

__title__ = "Layton's Text Processor - DLZ"
__version__ = "2.0"

def scandirs( path ):
    files = []
    for currentFile in glob.glob( os.path.join( path, '*' ) ):
        if os.path.isdir( currentFile ):
            files += scandirs( currentFile )
        else:
            files.append( currentFile )
    return files
    
def Extract(src, dst):

    table = normal_table( 'layton.tbl' )
    table.fill_with( '61=a', '41=A', '30=0' )
    table.add_items( '0A= ' )
    
    path = os.path.join(src, 'rc/en')
    files = filter(lambda x: x.__contains__('.dlz'), scandirs(path))    

    for _, fname in enumerate(files):
        print fname
        
        path = fname[len(src):]
        fdirs = dst + path[:-len(os.path.basename(path))]
        if not os.path.isdir(fdirs):
            os.makedirs(fdirs) 
    
        fd = open( fname, "rb" )
        buff = lzss.uncompress( fd, 0x0 )
        fd.close()
        
        temp = mmap.mmap(-1, len(buff))        
        temp.write(buff)
        temp.seek(0)
            
        buff = array.array("c")                
        if "ht_elm.dlz" in fname:
            entries = struct.unpack("<H", temp.read(2))[0]
            hdr_size = struct.unpack("<H", temp.read(2))[0]
            plz_size = struct.unpack("<L", temp.read(4))[0]
            
            for _ in range(entries):
                buff.extend( "<%04X>" % struct.unpack("<H", temp.read(2))[0])
                for _ in range(46):
                    c = temp.read(1)
                    if c == "\x00":
                        continue
                    else:
                        if c not in table:
                            buff.extend("<%02X>" % ord( c ))
                        else:
                            buff.extend(table[c])
                buff.extend("\r\n!******************************!\r\n")            
            
        elif "nz_lst.dlz" in fname:                            
            entries = struct.unpack("<H", temp.read(2))[0]
            hdr_size = struct.unpack("<H", temp.read(2))[0]
            plz_size = struct.unpack("<L", temp.read(4))[0]
            
            for _ in range(entries):
                buff.extend( "<%04X>" % struct.unpack("<H", temp.read(2))[0])
                buff.extend( "<%04X>" % struct.unpack("<H", temp.read(2))[0])
                for _ in range(48):
                    c = temp.read(1)
                    if c == "\x00":
                        continue
                    else:
                        if c not in table:
                            buff.extend("<%02X>" % ord( c ))
                        else:
                            buff.extend(table[c])
                buff.extend( "<%04X>" % struct.unpack("<H", temp.read(2))[0])      
                buff.extend("\r\n!******************************!\r\n")
        elif "ev_lch.dlz" in fname:                            
            entries = struct.unpack("<H", temp.read(2))[0]
            hdr_size = struct.unpack("<H", temp.read(2))[0]
            plz_size = struct.unpack("<L", temp.read(4))[0]
            
            for _ in range(entries):
                buff.extend( "<%04X>" % struct.unpack("<H", temp.read(2))[0])
                buff.extend( "<%04X>" % struct.unpack("<H", temp.read(2))[0])
                for _ in range(48):
                    c = temp.read(1)
                    if c == "\x00":
                        continue
                    else:
                        if c not in table:
                            buff.extend("<%02X>" % ord( c ))
                        else:
                            buff.extend(table[c])
                buff.extend("\r\n!******************************!\r\n")
        
        elif "ht_rcp.dlz" in fname:
            entries = struct.unpack("<H", temp.read(2))[0]
            hdr_size = struct.unpack("<H", temp.read(2))[0]
            plz_size = struct.unpack("<L", temp.read(4))[0]
            
            for _ in range(entries):
                buff.extend( "<%04X>" % struct.unpack("<H", temp.read(2))[0])
                buff.extend( "<%04X>" % struct.unpack("<H", temp.read(2))[0])
                for _ in range(28):
                    c = temp.read(1)
                    if c == "\x00":
                        continue
                    else:
                        if c not in table:
                            buff.extend("<%02X>" % ord( c ))
                        else:
                            buff.extend(table[c])
                buff.extend("\r\n!------------------------------!\r\n")                                    
                for _ in range(192):
                    c = temp.read(1)
                    if c == "\x00":
                        continue
                    elif c == "\x0a":
                        buff.extend("\r\n")
                    else:
                        if c not in table:
                            buff.extend("<%02X>" % ord( c ))
                        else:
                            buff.extend(table[c])                            
                buff.extend("\r\n!******************************!\r\n")        
        
        
        
        if len(buff):
            output = open(fdirs + os.path.basename(path) + '.txt', 'wb')
            buff.tofile( output )
            output.close()
        


TEMPPATH = "../Arquivos Gerados"
ALLPATH = "../ROM Modificada/LAYTON2/data_lt2"
INPATH = "../Textos Traduzidos"

class TagBlock:
    Name = None
    Content = None

class TextBlock:
    Name = None
    Content = None

tagf = re.compile( r"(<.+?>)" )  # Outside Tag
tagv = re.compile( r"<(\w+|@\w+)\W?(\w*)>" )  # Inside Tag (Content)

def Insert(src, dst):
    table = normal_table( 'layton.tbl' )
    table.fill_with( '61=a', '41=A', '30=0' )
    # table.add_items( '0A= ' )
    # table.add_items( '3C=<' )
    # table.add_items( '3E=>' )
    table.set_mode( 'inverted' )

    txt_path = os.path.join(src, '')
    files = filter(lambda x: x.__contains__('.txt'), scandirs(txt_path))           
    
    print '>> Comprimindo e Inserindo Arquivos...'

    for txtname in files:
        head, tail  = os.path.split(txtname)
        with open( txtname, 'r' ) as textf:

            # Hora de empacotar essa bodega!!
            dataf = array.array("c")          
        
            if "ht_elm.dlz" in txtname:
                entries = 0
                buffer = array.array("c")
                text = ""
                for line in textf:                
                    line = line.strip( '\r\n' )
                    if line == '!******************************!':
                        buffer.extend( text )
                        buffer.extend( '\x00' * ( 48 - ( len( text ) % 48 ) ) )
                        text = ""                    
                        entries += 1
                    else:
                        count = 0
                        # Tratar o conteúdo da linha
                        splitted = filter( bool, tagf.split( line ) )
                        
                        target = len(splitted)
                        
                        while splitted:
                            content = splitted.pop( 0 )
                            count += 1
                            if tagv.match( content ):
                                values = filter( bool, tagv.split( content ) )
                                assert len( values ) > 0, "{0} - Invalid tag".format( content )
                                if len( values ) == 1:
                                    if len(values[0]) == 4:
                                        text += struct.pack("<H", int(values[0], 16))
                                    else:
                                        text += values[0]
                                else:
                                    raise ValueError( "{0} - Tag content bigger than 1".format( content ) )
                            else:                                
                                try:
                                    text += "".join( [table[c] for c in content] )
                                except:
                                    raise ValueError( content )

                                #buffer.extend( text )
                                #buffer.extend( '\x00' * ( 48 - ( len( text ) % 48 ) ) )
                
                dataf.extend( struct.pack( "<H", entries ) )
                dataf.extend( struct.pack( "<H", 8 ) )
                dataf.extend( struct.pack( "<L", 0x30 ) )
                dataf.extend( buffer )            
                        
            
            elif "ht_rcp.dlz" in txtname:
                entries = 0
                buffer = array.array("c")
                text = ""
                for line in textf:                
                    line = line.strip( '\r\n' )
                    if line == '!******************************!':
                        if len( text ) > 192:
                            print "Error! " , text
                            raw_input()
                        text = text[:-1]
                        buffer.extend( text )
                        buffer.extend( '\x00' * ( 192 - ( len( text ) % 192 ) ) )
                        text = ""                    
                        entries += 1
                    elif line == '!------------------------------!':
                        text = text[:-1]
                        buffer.extend( text )
                        buffer.extend( '\x00' * ( 32 - ( len( text ) % 32 ) ) )
                        text = ""
                    else:
                        count = 0
                        # Tratar o conteúdo da linha
                        splitted = filter( bool, tagf.split( line ) )
                        
                        target = len(splitted)
                        
                        while splitted:
                            content = splitted.pop( 0 )
                            count += 1
                            if tagv.match( content ):
                                values = filter( bool, tagv.split( content ) )
                                assert len( values ) > 0, "{0} - Invalid tag".format( content )
                                if len( values ) == 1:
                                    if len(values[0]) == 4:
                                        text += struct.pack("<H", int(values[0], 16))
                                    else:
                                        text += values[0]
                                else:
                                    raise ValueError( "{0} - Tag content bigger than 1".format( content ) )
                            else:                                
                                try:
                                    text += "".join( [table[c] for c in content] )
                                except:
                                    raise ValueError( content )
                                    
                        text += '\x0a'
                
                dataf.extend( struct.pack( "<H", entries ) )
                dataf.extend( struct.pack( "<H", 8 ) )
                dataf.extend( struct.pack( "<L", 0xe0 ) )
                dataf.extend( buffer )            
            
            elif "nz_lst.dlz" in txtname:
                entries = 0
                buffer = array.array("c")            
            
                for line in textf:                
                    line = line.strip( '\r\n' )
                    if line == '!******************************!':
                        entries += 1                            
                        
                    else:
                        count = 0
                        # Tratar o conteúdo da linha
                        splitted = filter( bool, tagf.split( line ) )
                        text = ""
                        target = len(splitted)
                        
                        while splitted:
                            content = splitted.pop( 0 )
                            count += 1
                            if tagv.match( content ):
                                values = filter( bool, tagv.split( content ) )
                                assert len( values ) > 0, "{0} - Invalid tag".format( content )
                                if len( values ) == 1:
                                    if len(values[0]) == 4:
                                        if count == target:
                                            buffer.extend( text )
                                            buffer.extend( '\x00' * ( 48 - ( len( text ) % 48 ) ) )  
                                        buffer.extend(struct.pack("<H", int(values[0], 16)))
                                    else:
                                        text += values[0]
                                else:
                                    raise ValueError( "{0} - Tag content bigger than 1".format( content ) )
                            else:                                
                                try:
                                    text += "".join( [table[c] for c in content] )
                                except:
                                    raise ValueError( content )

                                #buffer.extend( text )
                                #buffer.extend( '\x00' * ( 48 - ( len( text ) % 48 ) ) )

                                
                dataf.extend( struct.pack( "<H", entries ) )
                dataf.extend( struct.pack( "<H", 8 ) )
                dataf.extend( struct.pack( "<L", 54 ) )
                dataf.extend( buffer )                                   

            if len(dataf):
                buff = mmap.mmap(-1, len(dataf))
                buff.write( dataf )
                
                with open("teste.bin", "wb") as kk:      
                    dataf.tofile(kk)
                   
                ret = lzss.compress( buff )
                buff.close()

                filepath = dst + txtname[len(src):]
                path  = os.path.dirname( filepath )
                if not os.path.isdir( path ):
                    os.makedirs( path )

                output = open(filepath.replace('.txt', ''), 'wb')
                
                ret.tofile(output)       
                output.close()
                
                print '>> \'' + filepath.replace('.txt', '') + ' criado.'            
            #raw_input()

if __name__ == '__main__':
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
    
    # dump text
    if args.mode == "e":
        print "Unpacking text"
        Extract( args.src , args.dst )
    # insert text
    elif args.mode == "i": 
        print "Packing text"
        Insert( args.src , args.dst )
    else:
        sys.exit(1)
