import errno
import os

__all__ = [
    'mkdir_p',
    'create_parent_dir',
    'is_parent_dir_exist'
]

''' README

Equivalent to UNIX command: '$ mkdir -p'

Return: Nil
'''
def mkdir_p( path ):
    try: os.makedirs( path )
    except OSError as exc:
        if( exc.errno == errno.EEXIST and os.path.isdir( path ) ): pass
        else: raise IOError( f'Error while creating the folder with path: {path}' )

''' README

Create the parent folder for a given file path

Return: Nil
'''
def create_parent_dir( path ):
    if( not is_parent_dir_exist( path ) ):
        path_parent = os.path.dirname( path )
        os.makedirs( path_parent, exist_ok=True )

''' README

Check if parent dir exist.

Return: boolean value
'''
def is_parent_dir_exist( path ):
    path_parent = os.path.dirname( path )
    if( not os.path.exists( path_parent ) and os.path.isdir( path_parent ) ): return False
    else: return True