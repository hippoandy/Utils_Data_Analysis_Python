from utilsDAWS.log import logger
from utilsDAWS.file import file

import glob
import urllib.request

__all__ = [
    'download'
]

# function to download the files
def download( url, f_storage, f_name, f_type ):
    # create the logger
    l = logger( fname=r'dl_failed.log' )

    f_path = r'{}/{}'.format( f_storage, r'{}.{}'.format( f_name, f_type ) )
    file.mkdir_p( f_path )
    if( file.is_file_exist( f_path ) ):
        num = len( glob.glob( r'{}/{}'.format( f_storage, r'{}*'.format( f_name ) ) ) )
        f_path = r'{}/{}'.format( f_storage, r'{}_({}).{}'.format( f_name, (num + 1), f_type ) )

    try: urllib.request.urlretrieve( url, f_path )
    except: l.commit( type='error', msg=f'Failed to download: {url}' )


if __name__ == '__main__':
    pass