import os

__all__ = [ 'mkdir_p' ]

# check if parent dir exist
def mkdir_p( path ):
    path_parent = os.path.dirname( path )
    if( not os.path.exists( path_parent ) ):
        os.makedirs( path_parent, exist_ok=True )