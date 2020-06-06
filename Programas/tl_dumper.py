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

__title__ = "Layton's Text Processor - PLZ"
__version__ = "2.0"

def scandirs( path ):
    files = []
    for currentFile in glob.glob( os.path.join( path, '*' ) ):
        if os.path.isdir( currentFile ):
            files += scandirs( currentFile )
        else:
            files.append( currentFile )
    return files
    
def Extract():

    table = normal_table( 'layton.tbl' )
    table.fill_with( '61=a', '41=A', '30=0' )
    table.add_items( '0A= ' )

    for folder in FOLDERS:
        print folder
        current_path = os.path.join( FULL_PATH, folder )
        filelist = scandirs( current_path )

        for f in filelist:
            fd = open( f, "rb" )
            temp = open( 'temp', 'w+b' )

            buff = lzss.uncompress( fd, 0x0 )
            buff.tofile( temp )
            fd.close()
            # sys.exit( 0 )
            # continue
            p, h = os.path.split( f )
            p = os.path.join( OUTPATH, p[len( FULL_PATH ) + 1:] )
            if not os.path.isdir( p ):
                os.makedirs( p )

            outpath = "{0}.txt".format( os.path.join( p, h ) )
            out = open( outpath, "w" )

            temp.seek( 0, 0 )
            header = struct.unpack( "<4L", temp.read( 16 ) )
            # Verificações iniciais
            print f
            assert header[0] == 0x10
            assert header[1] == os.path.getsize( temp.name )
            assert header[2] == 0x324b4350  # PCK2
            assert header[3] == 0

            while True:
                curr = temp.tell()

                file_header = struct.unpack( "<4L", temp.read( 16 ) )
                file_name = temp.read( file_header[0] - 16 ).replace( '\x00', '' )

                # data = temp.read(file_header[3]+1)

                out.write( "[{0}]\n".format( file_name ) )
                data = ""
                if ".gds" in file_name:
                    data_size = struct.unpack( "<L", temp.read( 4 ) )[0]
                    data_pointer = temp.tell()
                # Replace data
                # Estruturas de arquivos
                    while temp.tell() < ( data_pointer + data_size ):
                        b = temp.read( 1 )
                        # Tratamento das tags dos cabeçalhos
                        if b in ( "\x01", "\x03", "\x0c" ):
                            b += temp.read( 1 )
                            if b == "\x01\x00":
                                content = struct.unpack( "<L", temp.read( 4 ) )[0]
                                data += "<01:%08X>" % content
                            elif b == "\x03\x00":
                                content_length = struct.unpack( "<H", temp.read( 2 ) )[0]
                                data += "<03:{0}>".format( content_length )
                                while True:
                                    c = temp.read( 1 )
                                    if c == "\x00":
                                        break
                                    elif c in ( "@", ):
                                        c += temp.read( 1 )
                                        if c == "@B":
                                            # texto contínuo, ou com quebra de linhas
                                            #data += " "
                                            data += "\n"
                                        elif c == "@p":
                                            data += "<W>"
                                        elif c == "@c":
                                            data += "\n!------------------------------!\n"
                                        else:
                                            data += "<{0}>".format( c )
                                    elif c not in table:
                                        data += "<%02X>" % ord( c )
                                    else:
                                        data += table[c]
                            elif b == "\x0c\x00":
                                data += '\n!******************************!\n'
                                break
                            else:
                                raise TypeError( "Unknown tag", b )
                elif ".txt" in file_name:
                    data_size = file_header[3]

                    while True:
                        c = temp.read( 1 )
                        if c == "\x00":
                            data += '\n!******************************!\n'
                            break
                        elif c == "\x0a":
                            # texto contínuo, ou com quebra de linhas
                            data += "\n"
                            #data += " "
                        elif c not in table:
                            data += "<%02X>" % ord( c )
                        else:
                            data += table[c]
                elif ".dat" in file_name:
                    data += "<%04d>" % struct.unpack( "<H", temp.read( 2 ) )[0]
                    temp.read(2)
                    data += temp.read(48).replace('\0','') + '\n'
                    for c in temp.read(12): # ??
                        data += "<%02X>" % ord(c)
                    data += '\n'
                    
                    ptr = struct.unpack("<12L", temp.read(48))
                    base = ptr[0]
                    for x in ptr[1:]:
                        if x > base:
                            data_size = x-base
                            for _ in range(data_size):
                                c = temp.read( 1 )
                                if c == "\x00":
                                    data += '\n!******************************!\n'
                                    break
                                elif c == "\x0a":
                                    # texto contínuo, ou com quebra de linhas
                                    data += "\n"
                                    #data += " "
                                elif c not in table:
                                    data += "<%02X>" % ord( c )
                                else:
                                    data += table[c]
                        else:
                            while True:
                                c = temp.read( 1 )
                                if c == "\x00":
                                    data += '\n!******************************!\n'
                                    break
                                elif c == "\x0a":
                                    # texto contínuo, ou com quebra de linhas
                                    data += "\n"
                                    #data += " "
                                elif c not in table:
                                    data += "<%02X>" % ord( c )
                                else:
                                    data += table[c]
                                                
                            break
                        base = x

                out.write( data )
                temp.seek( curr + file_header[1] )

                if temp.tell() == header[1]:
                    break

            out.close()
            temp.close()

            os.unlink( temp.name )

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
tagv = re.compile( r"<(\w+|@\w+|\-)\W?(\w*)>" )  # Inside Tag (Content)

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
            if not "plz" in txtname:
                continue
    
            head, tail  = os.path.split(txtname)
            with open( txtname, 'r' ) as textf:

                blocks = []
                
                bFirstLine = False
                bSecondLine  = False
                textb = None
                
                tag = TagBlock()
                tag.Content = array.array('c')

                for line in textf:
                    line = line.strip( '\r\n' )
                    if line.startswith( '[' ) and line.endswith( ']' ):
                        if textb:
                            blocks.append( textb ) 
                    
                        textb = TextBlock()
                        textb.Content = list()
                        textb.Name = line[1:-1]
                        textb.Name = textb.Name + '\x00' * ( 4 - ( len( textb.Name ) % 4 ) )
                        tag = TagBlock()
                        tag.Content = array.array( 'c' )
                        bFirstLine = True
                        
                    elif line == '!------------------------------!':
                        tag.Content.pop()
                        tag.Content.pop()
                        tag.Content.extend( "@c" )
                    elif line == '!******************************!':
                        if "nazo" in tail:
                            if len( tag.Content ) > 0:
                                tag.Content.pop()                          
                            tag.Content.extend( '\x00' )
                            textb.Content.append( tag )                        
                            tag = TagBlock()
                            tag.Content = array.array( 'c' )
                        elif ".txt" in textb.Name:
                            tag.Content.pop()
                            textb.Content.append( tag )
                            #blocks.append( textb )                            
                        else:
                            tag.Content.pop()
                            tag.Content.pop()
                            textb.Content.append( tag )
                            tag = TagBlock()
                            tag.Name = 0x0C
                            textb.Content.append( tag )
                            #blocks.append( textb )                            
                        
                    else:
                        # Tratar o conteúdo da linha
                        splitted = filter( bool, tagf.split( line ) )
                        while splitted:
                            content = splitted.pop( 0 )
                            if tagv.match( content ):                            
                                values = filter( bool, tagv.split( content ) )
                                assert len( values ) > 0, "{0} - Invalid tag".format( content )
                                if len( values ) == 1:
                                    if len(values[0]) == 2:
                                        try:
                                            h = chr( int( values[0], 16 ) )
                                            if bSecondLine:
                                                tag.Content.extend( h )
                                            else:
                                                if h in table:
                                                    tag.Content.extend( table[h] )
                                                else:
                                                    tag.Content.extend( h )
                                        except:
                                            if values[0].startswith("@"):
                                                tag.Content.extend( values[0] )
                                            else:
                                                tag.Content.extend( "<"+values[0]+">" )
                                    elif len(values[0]) == 4:
                                        if values[0] == "HOLD":
                                            tag.Content.extend( '<'+values[0]+'>' )
                                        else:
                                            h = struct.pack("<H", int(values[0]))
                                            tag.Content.extend( h + "\x70\x00" )
                                    else:
                                        if values[0] == "W":
                                            tag.Content.extend( "@p" )
                                        elif values[0] in ( "3C", "3E" ):
                                            tag.Content.extend( table[chr( int( values[0], 16 ) )] )
                                        elif values[0] in ("-",):
                                            tag.Content.extend( "<"+values[0]+">" )
                                        else:
                                            tag.Content.extend( values[0] )
                                        
                                elif len( values ) == 2:
                                    if isinstance( tag, TagBlock ):
                                        textb.Content.append( tag )

                                    tag = TagBlock()
                                    tag.Content = array.array( 'c' )                                        
                                    if values[0] == "01":
                                        tag.Name = 0x01
                                        tag.Content.extend( struct.pack( "<L", int( values[1], 16 ) ) )
                                    elif values[0] == "03":
                                        tag.Name = 0x03
                                    else:
                                        raise ValueError( "{0} - Unknown tag".format( content ) )
                                else:
                                    raise ValueError( "{0} - Tag content bigger than 2".format( content ) )
                            else:
                                 
                                
                                #assert tag.Name == 0x03 , "{0} - Missing \\x03".format( line )

                                try:
                                    text = "".join( [table[c] for c in content] )
                                except:
                                    raise ValueError( content )

                                tag.Content.extend( text )
                                
                                if "nazo" in tail:
                                    if bFirstLine:
                                        tag.Content.extend( '\x00' * ( 48 - ( len( text ) % 48 ) ) )
                        
                        #
                        if "nazo" in tail:
                            if not bFirstLine:
                                tag.Content.extend( "\x0a" )
                        
                            if bSecondLine:
                                tag.Content.pop()
                                textb.Content.append( tag )
                                tag = TagBlock()
                                tag.Content = array.array( 'c' )
                                bSecondLine = False
                        
                            if bFirstLine:
                                bSecondLine = True
                            
                            bFirstLine = False
                        else:
                            if ".txt" in textb.Name:
                                tag.Content.extend( "\x0a" )
                            else:
                                tag.Content.extend( "@B" )
                        
            if textb:
                blocks.append( textb )     
                
            # Hora de empacotar essa bodega!!
            dataf = array.array("c")
            # ponteiros
            for block in blocks:
                if "nazo" in tail:
                    datab = array.array( "c" )
                    ptr = []
                    for k, tag in enumerate(block.Content):
                        if k >= 1:
                            ptr.append( len(tag.Content) )
                        
                    for k, tag in enumerate(block.Content):
                        if k == 0:
                            datab.extend( tag.Content )
                            for p in range( 12 ):
                                try:
                                    if p == 0 or p > (len(ptr)-1):
                                        datab.extend(struct.pack("<L", 0) )
                                    else:
                                        datab.extend(struct.pack("<L", reduce(lambda x,y:x+y, ptr[:p])))
                                except:
                                    datab.extend(struct.pack("<L", 0) )
                        else:
                            datab.extend( tag.Content )
                else:
                    datab = array.array( "c" )
                    for tag in block.Content:                        
                        if tag.Name == 0x01:
                            datab.extend( struct.pack( "<H", tag.Name ) )
                            datab.extend( tag.Content )
                        elif tag.Name == 0x03:
                            tag.Content.extend( '\x00' )
                            datab.extend( struct.pack( "<H", tag.Name ) )
                            datab.extend( struct.pack( "<H", len( tag.Content ) ) )
                            datab.extend( tag.Content )
                        elif tag.Name == 0x0C:
                            datab.extend( struct.pack( "<H", tag.Name ) )
                        else:
                            datab.extend( tag.Content )
                            

                padding = ( 4 - len( datab ) % 4 )
                datab.extend( "\x00" * padding )  # U32 align                     

                # Header                
                if "nazo" in tail:
                    dataf.extend( struct.pack( "<L", 16 + len( block.Name ) ) )
                    dataf.extend( struct.pack( "<L", 16 + len( block.Name ) + len( datab ) ) )
                    dataf.extend( struct.pack( "<L", 0 ) )
                    dataf.extend( struct.pack( "<L", len( datab ) - padding ) )
                    dataf.extend( block.Name )
                    dataf.extend( datab )                    
                elif ".txt" in block.Name:
                    dataf.extend( struct.pack( "<L", 16 + len( block.Name ) ) )
                    dataf.extend( struct.pack( "<L", 16 + len( block.Name ) + len( datab ) ) )
                    dataf.extend( struct.pack( "<L", 0 ) )
                    dataf.extend( struct.pack( "<L", len( datab ) - padding ) )
                    dataf.extend( block.Name )
                    dataf.extend( datab )
                    #dataf.write( "\x00" * padding )  # U32 align                        
                else:
                    dataf.extend( struct.pack( "<L", 16 + len( block.Name ) ) )
                    dataf.extend( struct.pack( "<L", 16 + len( block.Name ) + 4 + len( datab ) ) )
                    dataf.extend( struct.pack( "<L", 0 ) )
                    dataf.extend( struct.pack( "<L", 4 + len( datab ) - padding ) )
                    dataf.extend( block.Name )
                    dataf.extend( struct.pack( "<L", len( datab ) - padding ) )
                    dataf.extend( datab )                    

            buff = mmap.mmap(-1, len(dataf) + 16)
            buff.write( struct.pack( "<L", 0x10 ) )
            buff.write( struct.pack( "<L", 0x10 + len( dataf ) ) )
            buff.write( struct.pack( "<L", 0x324b4350 ) )
            buff.write( struct.pack( "<L", 0 ) )
            buff.write( dataf )
            
            with open("teste.bin", "wb") as kk:
                kk.write( struct.pack( "<L", 0x10 ) )
                kk.write( struct.pack( "<L", 0x10 + len( dataf ) ) )
                kk.write( struct.pack( "<L", 0x324b4350 ) )
                kk.write( struct.pack( "<L", 0 ) )            
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
