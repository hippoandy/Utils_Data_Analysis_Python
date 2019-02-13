from pathlib import Path
import os

__all__ = [
    'is_file_exist',
    'check_file_exist',
    'rm_file'
]

def check_file_exist( path ):
    f = Path( path )
    if( f.is_file() ): pass
    else: raise IOError( f'File {path} not exists!' )

def is_file_exist( path ):
    f = Path( path )
    if( f.is_file() ): return True
    else: return False

def rm_file( fpath ):
    if( os.path.isfile( fpath ) ): os.remove( fpath )