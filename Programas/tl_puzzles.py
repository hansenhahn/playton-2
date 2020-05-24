#!/usr/bin/env python
# -*- coding: windows-1252 -*-
'''
Created on 23/12/2017

@author: Hansen
'''

import os
import sys
import re

__title__ = "Layton's Puzzle Splitter"
__version__ = "2.0"

TARGET = [ "nazo1" , "nazo2" , "nazo3" ] 
PLZ_FORMAT = "{0}.plz.txt"
TXT_FORMAT = "{0}.txt"

PATH = r'../ROM Original/Splitted/LAYTON2/data_lt2'

UNPACK_INPUT_PATH = r'../Textos Traduzidos/plz/nazo/en'
UNPACK_OUTPUT_PATH = r'../Textos Traduzidos DELETAR/puzzles_splitted'

PACK_INPUT_PATH = r'../Textos Traduzidos/puzzles_splitted'
PACK_OUTPUT_PATH = r'../Textos Traduzidos/nazo/en'  

TAG = re.compile( r"(\[.+?\])" ) 

def Unpack():
    
    for target in TARGET:
    
        input = os.path.join( UNPACK_INPUT_PATH , PLZ_FORMAT.format( target ) )
        
        output_path = os.path.join( UNPACK_OUTPUT_PATH , target )
        if not os.path.isdir( output_path ):
            os.makedirs( output_path )

        print "Splitting %s" % target
            
        with open( input , "r" ) as fd:
            ret = TAG.split( fd.read() )[1:]            
            for i, data in enumerate(ret) :
                if (i % 2) == 0:
                    output = os.path.join( output_path , TXT_FORMAT.format( data ) )
                else:
                    with open( output , "w" ) as out:
                        out.write( data[1:-1] )
    
def Pack():
    pass
    

if __name__ == "__main__":
    import argparse
    
    os.chdir( sys.path[0] )
    os.system( 'cls' )

    print "{0:{fill}{align}70}".format( " {0} {1} ".format( __title__, __version__ ) , align = "^" , fill = "=" )
    
    Unpack()