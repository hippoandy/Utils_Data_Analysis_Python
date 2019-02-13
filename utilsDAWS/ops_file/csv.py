import json, textwrap
import glob, os
import pandas as pd

from utilsDAWS import ops_data as ops
from utilsDAWS import ops_file as rw
from utilsDAWS import config

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

def json_to_csv( d_path, r_path_f, e_path_f, header="", encode="utf-8" ):
    if( header == "" ):
        print( textwrap.dedent( f'''
            Please specify the csv header in comma seperated string!
            Abort Operations!
        '''))
        return
    # make sure the data folder exists
    rw.mkdir_p( r_path_f )
    # open result data file
    f = open( r_path_f, 'w', encoding=encode, errors='ignore' )
    f.write( '{}\n'.format( header ) )
    # get all the data files
    err = []
    for n in glob.glob( d_path ):
        if( 'err' in n ): continue
        content = json.loads( open( n, 'r', encoding=encode, errors='ignore' ).read() )
        if( not ops.empty_struct( content ) ):
            for e in content:
                length = len( header.split( ',' ) )
                dpoint = [ '' ] * length
                i = 0
                # for k in e.keys():
                for k in header.split( ',' ):
                    if( k in e.keys() ):
                        # prevent from id become a numeric value
                        if( 'id' in k ): dpoint[ i ] = '"{}"'.format( str(e[ k ]) )
                        elif( ops.is_numeric( str(e[ k ]) ) ): dpoint[ i ] = str(e[ k ])
                        else: dpoint[ i ] = ops.comma_to_hyphen( str(e[ k ]) )
                    else: dpoint[ i ] = ""
                    i += 1
                    if( i == length ): break
                try:
                    f.write( '{}\n'.format( ','.join( dpoint ) ) )
                except: err.append( e )

    if( not ops.empty_struct( err ) ):
        rw.mkdir_p( e_path_f )
        rw.write_to_log_json( e_path_f, err )
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

'''README

Combine multiple csv format files into one.

Return: Nil

'''
def combine_csv_files( dir_files=config.path_data, files=config.f_data_csv, dir_result=config.path_data, result=config.f_combine_csv, encode=config.encoding_f ):
    # delete old combined result file
    pre = r'{}/{}'.format( dir_result, result )
    if( os.path.isfile( pre ) ): os.remove( pre )

    # start the combination
    list_ = []
    for n in glob.glob( r'{}/{}'.format( dir_files, files ) ):
        if( 'err' in str(n) ): continue # prevent from reading the log files

        df = pd.read_csv( n, header=0, encoding=config.encoding_f )
        list_.append( df )

    df = pd.concat( list_, axis=0, ignore_index=True )
    df.to_csv( '{}/{}'.format( dir_result, result ), encoding=encode, index=False )

if __name__ == '__main__':
    pass
