''' README

Cleaning empty log files created by the scraper

Author: Yu-Chang Ho
'''

import glob, os, time
import textwrap
import argparse

from utilsDAWS import config
from utilsDAWS import ops_data as ops
from utilsDAWS import ops_file as rw
from utilsDAWS.ops_thread import requester

# parameters ------------------------------------------------------
path = config.path_data
name_task = config.n_scrape_clean


tar = ops.invalid_val()
f_result_error = ops.invalid_val()

concurrent = config.concurrent
timeout = config.timeout
# ------------------------------------------------------ parameters

__all__ = [
    'cleaner'
]

# init
class cleaner():
    ''' multi-threading scraper '''
    def __init__( self, attemp_access=False, flag='deletable', name=config.n_scrape_clean, concurrent=config.concurrent, timeout=config.timeout ):
        self.name = name
        self.concurrent = concurrent
        self.timeout = timeout

        # if the user wish to test the accessiblility of the failed URLs
        self.attemp_access = attemp_access
        self.flag = flag
        self.requester = None

    def init_requester( self, concurrent=concurrent, timeout=timeout, run_with=None ):
        self.requester = requester( name=self.name, flag=self.flag, timeout=timeout, concurrent=concurrent )
        self.requester.init()
        self.requester.run_with( run_with )
        return self

    def clean_log( self, dir_logs=config.path_data, logs=config.f_log_sc_json,\
        dir_result=config.path_data, result=config.f_result_clean_log_json ):

        # delete old concated result data
        rw.rm_file( r'{}/{}'.format( dir_result, result ) )

        c = 1
        for f in glob.glob( r'{}{}'.format( dir_logs, logs ) ):
            content = rw.read_from_json( f )
            error = []
            if( not ops.empty_struct( content ) ):
                if( self.attemp_access ):
                    print( textwrap.dedent( f'''
                        Non-empty Log file: {str(f)}
                            Attempt to access the URLs again......
                    '''))
                    # TO-DO
                    # determine the name of tmp files

                    self.requester.input( content ).run()

                    for e in content:
                        if( e[ self.flag ] ): continue # if the URL is marked to be deletable
                        error.append( e )

                    # if no error exists anymore, delete the log file
                    if( not ops.empty_struct( error ) ):
                        print( textwrap.dedent( f'''
                            Still have items that not able to be removed......
                                Numbuer of remaining items: {len( error )}
                                Operation completed for file: {f}
                            --------------------------------------------------
                        ''') )
                        rw.write_to_log_json( '{}/{}_{}.json'.format( dir_logs, self.name, c ), error )
                    os.remove( r"{}".format( f ) )
                else:
                    print( textwrap.dedent( f'''
                        Non-empty Log file: {str(f)}
                            Not deleting this file since its not empty
                    '''))
            else:
                print( textwrap.dedent( f'''
                    No content of Log file: {str(f)}
                        Deleting this file......
                '''))
                os.remove( r"{}".format( f ) )
            # pause the program a little bit
            # time.sleep( 1 )
            c += 1

        if( self.attemp_access ):
            # merge the result into a single file
            still_errs = glob.glob( r'{}/{}_*.json'.format( dir_result, self.name ) )
            if( not ops.empty_struct( still_errs ) ):
                print( textwrap.dedent( f'''
                    Starting to merge the remain error log into a single file:
                        Number of file to be merged: {len( still_errs )}
                ''') )
                error = []
                for f in still_errs:
                    content = rw.read_from_json( f )
                    if( not ops.empty_struct( content ) ): error += [ e[ 'url' ] for e in content ]
                    # delete the file
                    os.remove( r"{}".format( f ) )

                print( textwrap.dedent( f'''
                    Merge completed!
                    Original number of still error items: {len( error )}
                        Trying to delete duplicated entries......
                ''') )
                # delete duplicate items
                error = ops.list_deduplicated( error )
                commitment = r'{}/{}'.format( path, f_result_error )
                print( textwrap.dedent( f'''
                    Completed!
                    Remaining items: {len( error )}
                        Commit the remaining items into file: {commitment}
                ''') )
                # commit to a new log file
                rw.write_to_log_json( commitment, error )

        print( "Process Completed!" )

# the main function
if __name__ == '__main__':
    pass