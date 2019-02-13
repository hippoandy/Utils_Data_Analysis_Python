from pathlib import Path

__all__ = [
    'is_file_exist',
    'check_file_exist'
]

def check_file_exist( path ):
    f = Path( path )
    if( f.is_file() ): pass
    else: raise IOError( f'File {path} not exists!' )

def is_file_exist( path ):
    f = Path( path )
    if( f.is_file() ): return True
    else: return False