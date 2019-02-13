import json, textwrap
import os, glob

from utilsDAWS import ops_data as ops
from utilsDAWS import config

__all__ = [
    'write_to_json', 'read_from_json', 'save_as_json', 'load_json',
    'write_to_log_json',
    'concat_json_files'
]

def write_to_json( path, data, encode='utf-8' ):
    ''' write json to current dir, path="out path", data="json serializable data" '''
    parent = os.path.dirname( path )
    if( not (os.path.exists( parent ) and os.path.isdir( parent )) ):
        os.makedirs(parent)
    with open( path, 'w+', encoding=encode, errors='ignore' ) as f:
        json.dump( data, f )

save_as_json = write_to_json

def read_from_json( path, encode='utf-8' ):
    ''' return data from json, path="read path" '''
    with open( path, 'r', encoding=encode, errors='ignore' ) as f:
        return json.load( f )

load_json = read_from_json

# write error data in json format to log
def write_to_log_json( path, data, encode='utf-8' ):
    write_to_json( path, data, encode )

'''README

Combine multiple csv format files into one.

Return: Nil
'''
def concat_json_files( dir_files=config.path_data, files=config.f_data_json, dir_result=config.path_data, result=config.f_concated_json, encode=config.encoding_f ):
    concated = []
    for n in glob.glob( r'{}/{}'.format( dir_files, files ) ):
        if( 'err' in str(n) ): continue # prevent from reading the log files
        # get the item urls
        content = None
        with open( n ) as f:
            try: content = json.loads( f.read() )
            except:
                print( f'''File {n} is not well formated! Skip to the next file......''' )
                continue
        if( ops.empty_struct( content ) or content == None ):
            print( f'''No content of file: {str(n)}! Skip to the next file......''' )
            continue
        concated += content
    # commit the result
    write_to_json( r'{}/{}'.format( dir_result, result ), concated )

if __name__ == '__main__':
    pass
