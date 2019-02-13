import os

__all__ = [ 'mkdir_p', 'is_parent_dir_exist' ]

''' README

Equivalent to UNIX command: '$ mkdir -p'

Return: Nil
'''
def mkdir_p( path ):
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