''' utils for json r/w '''

import json
import os

__all__ = [
    'write_to_json', 'read_from_json', 'save_as_json', 'load_json',
    'write_to_log_json'
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
    with open( path, 'rb', encoding=encode, errors='ignore' ) as f:
        return json.load( f )

load_json = read_from_json


# write error data in json format to log
def write_to_log_json( path, data, encode='utf-8' ):
    write_to_json( path, data, encode )


if __name__ == '__main__':
    pass
