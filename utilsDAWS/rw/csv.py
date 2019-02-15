import json, textwrap
import os, glob, sys
import pandas as pd

from utilsDAWS import config
from utilsDAWS import rw
from utilsDAWS import store
from utilsDAWS import value as val

__all__ = [
    'json_to_csv', 'list_to_csv',
    'concat_csv_files'
]

''' README

Convert the json format data into csv

Input:
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
    store.mkdir_p( r_path_f )
    # open result data file
    f = open( r_path_f, 'w', encoding=encode, errors='ignore' )
    f.write( '{}\n'.format( header ) )
    # get all the data files
    err = []
    for n in glob.glob( d_path ):
        if( 'err' in n ): continue
        content = json.loads( open( n, 'r', encoding=encode, errors='ignore' ).read() )
        if( not val.empty_struct( content ) ):
            for e in content:
                length = len( header.split( ',' ) )
                dpoint = [ '' ] * length
                i = 0
                # for k in e.keys():
                for k in header.split( ',' ):
                    if( k in e.keys() ):
                        # prevent from id become a numeric value
                        if( 'id' in k ): dpoint[ i ] = '"{}"'.format( str(e[ k ]) )
                        elif( val.is_numeric( str(e[ k ]) ) ): dpoint[ i ] = str(e[ k ])
                        else: dpoint[ i ] = val.comma_to_hyphen( str(e[ k ]) )
                    else: dpoint[ i ] = ""
                    i += 1
                    if( i == length ): break
                try:
                    f.write( '{}\n'.format( ','.join( dpoint ) ) )
                except: err.append( e )

    if( not val.empty_struct( err ) ):
        store.mkdir_p( e_path_f )
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
def concat_csv_files( dir_files=config.path_data, files=config.f_data_csv, dir_result=config.path_data, result=config.f_concated_csv, encode=config.encoding_f ):
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
    df.to_csv( r'{}/{}'.format( dir_result, result ), encoding=encode, index=False )

def merge_csv_files(\
    dir_files=config.path_data,\
    file_1='', file_2='',\
    encode_f=config.encoding_f,
    dir_result=config.path_data, result=config.f_merged_csv,\
    encode_result=config.encoding_f,\
    list_col=[] ):

    # error handling
    if( file_1 == '' or file_2 == '' ):
        print( textwrap.dedent( f'''
            Required two files for the merge!
            You give:
                - file 1: {file_1}
                - file 2: {file_2}
        ''' ) )
        sys.exit()
    if( val.empty_struct( list_col ) ):
        print( f'''Please specify the column for merge!''' )
        sys.exit()

    path_1 = r'{}/{}'.format( dir_files, file_1 )
    path_2 = r'{}/{}'.format( dir_files, file_2 )

    store.check_file_exist( path_1 )
    store.check_file_exist( path_2 )

    # start the operation
    df1 = pd.read_csv( path_1, header=0, encoding=encode_f )
    df2 = pd.read_csv( path_2, header=0, encoding=encode_f )

    df = pd.merge( df1, df2, on=list_col )

    # commit the result
    df.to_csv( '{}{}'.format( dir_result, result ), encoding=encode_result, index=False )

if __name__ == '__main__':
    pass
