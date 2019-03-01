import errno
import os

__all__ = [
    'mkdir_p',
    'create_parent_dir',
    'is_dir_exist',
    'is_parent_dir_exist',
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

Create the folder for a given folder path

Return: Nil
'''
def create_dir( path ):
    mkdir_p( path )

''' README

Create the parent folder for a given file path

Return: Nil
'''
def create_parent_dir( path ):
    if( not is_parent_dir_exist( path ) ):
        path_parent = os.path.dirname( path )
        mkdir_p( path_parent )

''' README

Check if dir exist.

Return: boolean value
'''
def is_parent_dir_exist( path ):
    if( os.path.exists( path ) ): return True
    else: return False

''' README

Check if parent dir exist.

Return: boolean value
'''
def is_parent_dir_exist( path ):
    path_parent = os.path.dirname( path )
    if( not os.path.exists( path_parent ) ): return False
    else: return True