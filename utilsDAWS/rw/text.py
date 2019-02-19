import glob

import sys
sys.path.append( '..' )
import config

__all__ = [
    'write_to_text',
    'write_to_log_text',
    'concat_text_files'
]

'''README

Write plain text data into a file.

Return: data file commitment
'''
def write_to_text( path, data, encode='utf-8' ):
    f = open( path, 'w+', encoding=encode )
    f.write( data )
    f.close()

'''README

Write log in plain text format to a file.

Return: data file commitment
'''
def write_to_log_text( path, data, encode='utf-8' ):
    write_to_text( path, data, encode=encode )

'''README

Combine multiple text files into one.

Return: data file commitment
'''
def concat_text_files( dir_files=config.path_data, files=config.f_data_txt, \
    dir_result=config.path_data, result=config.f_concated_txt, \
    encode=config.encoding_f, \
    del_origin=False, del_empty=False ):

    with open( r'{}/{}'.format( dir_result, result ), 'r', encoding=encode ) as result:
        for n in glob.glob( r'{}/{}'.format( dir_files, files ) ):
            f = open( n, 'r', encoding=encode )
            for l in f.readlines(): result.write( l + '\n' )
    result.close()

if __name__ == '__main__':
    pass