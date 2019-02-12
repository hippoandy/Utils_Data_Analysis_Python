import json, textwrap
import glob, os

from utils import ops_data, ops_file

__all__ = [
    'json_to_csv', 'list_to_csv'
]

# write the data from json to csv format file
''' README

convert the json format data into csv

Parameters:
    d_path: path for data files (could be multiple files)
    r_path_f: the result file location
    e_path_f: if error present, the data point will be store in this file
    header: the csv file header

Author: Yu-Chang Ho (Andy)
'''

# check if parent dir exist
def parent_dir_exist( path ):
    path_parent = os.path.dirname( path )
    if( not os.path.exists( path_parent ) and os.path.isdir( path_parent ) ):
        os.makedirs( path_parent, exist_ok=True )

def json_to_csv( d_path, r_path_f, e_path_f, header="", encode="uft-8" ):
    if( header == "" ):
        print( textwrap.dedent( f'''
            Please specify the csv header in comma seperated string!
            Abort Operations!
        '''))
        return
    # make sure the data folder exists
    parent_dir_exist( r_path_f )
    # open result data file
    f = open( r_path_f, 'w', encoding=encode, errors='ignore' )
    f.write( '{}\n'.format( header ) )
    # get all the data files
    err = []
    for n in glob.glob( d_path ):
        if( 'err' in n ): continue
        content = json.loads( open( n, 'r', encoding=encode, errors='ignore' ).read() )
        if( not ops_data.empty_struct( content ) ):
            for e in content:
                length = len( header.split( ',' ) )
                dpoint = [ '' ] * length
                i = 0
                # for k in e.keys():
                for k in header.split( ',' ):
                    if( k in e.keys() ):
                        # prevent from id become a numeric value
                        if( 'id' in k ): dpoint[ i ] = '"{}"'.format( str(e[ k ]) )
                        elif( ops_data.is_numeric( str(e[ k ]) ) ): dpoint[ i ] = str(e[ k ])
                        else: dpoint[ i ] = ops_data.comma_to_hyphen( str(e[ k ]) )
                    else: dpoint[ i ] = ""
                    i += 1
                    if( i == length ): break
                try:
                    f.write( '{}\n'.format( ','.join( dpoint ) ) )
                except: err.append( e )

    if( not ops_data.empty_struct( err ) ):
        parent_dir_exist( e_path_f )
        ops_file.write_to_log_json( e_path_f, err )
    f.close()

def list_to_csv( path, list_, header='', encode='utf-8' ):
    ''' write json to current dir, path="out path", data="json serializable data" '''
    parent = os.path.dirname( path )
    if( not (os.path.exists( parent ) and os.path.isdir( parent )) ):
        os.makedirs(parent)

    def append_newline( f, text ):
        if( '\n' not in text ): f.write( '\n' )

    with open( path, 'w+', encoding=encode, errors='ignore' ) as f:
        if( header != '' ):
            f.write( header )
            append_newline( f, header )
        for l in list_:
            f.write( l )
            append_newline( f, l )
        f.close()

if __name__ == '__main__':
    pass
