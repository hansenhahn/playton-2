#!/usr/bin/env python
# -*- coding: windows-1252 -*-
'''
Created on 17/04/2018

@author: diego.hahn
'''

import time
import re
import glob
import os.path
import struct
import array
import sys
import mmap

if __name__ == '__main__':
    import argparse
    
    os.chdir( sys.path[0] )

    parser = argparse.ArgumentParser()
    parser.add_argument( '-s0', dest = "src0", type = str, nargs = "?", required = True )
    parser.add_argument( '-s1', dest = "src1", type = str, nargs = "?", required = True )
    parser.add_argument( '-n', dest = "num", type = int , required = True )
    
    args = parser.parse_args()
    
    print "Updating overlay for file number {0}".format( args.num )
    
    with open( args.src1 , "rb" ) as fd:
        fd.seek( 0, 2 )    

        size0 = fd.tell()   # Tamanho comprimido   
        fd.seek( -8, 1 )    
        header3, header1 = struct.unpack('<LL', fd.read(8))
        header3 = header3 & 0x00FFFFFF
        
        size1 = header1 + header3          # Tamanho descomprimido
                  
    with open( args.src0 , "r+b" ) as fd:
        fd.seek( args.num * 0x20 + 8 )
        fd.write( struct.pack( "<L", size1 ) )
        
        fd.seek( args.num * 0x20 + 28 )
        fd.write( struct.pack( "<L", size0 | 0x01000000 ) )
