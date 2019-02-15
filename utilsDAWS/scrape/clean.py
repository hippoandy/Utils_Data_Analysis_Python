''' README

Cleaning empty log files created by the scraper

Author: Yu-Chang Ho
'''

from utilsDAWS import config
from utilsDAWS import value as val
from utilsDAWS.request import requester
from utilsDAWS import rw
from utilsDAWS import store
from utilsDAWS.stdout import report

import glob, time
import textwrap
import argparse

# parameters ------------------------------------------------------
path = config.path_data
name_task = config.n_scrape_clean


tar = val.invalid_val()
f_result_error = val.invalid_val()

concurrent = config.concurrent
timeout = config.timeout
# ------------------------------------------------------ parameters

__all__ = [
    'cleaner'
]

# init
class cleaner():
    ''' multi-threading scraper '''
    def __init__( self, attemp_access=False, flag='deletable', name=config.n_scrape_clean ):
        self.name = name

        # if the user wish to test the accessiblility of the failed URLs
        self.attemp_access = attemp_access
        self.flag = flag
        self.requester = None

    def init_requester( self, run_with, concurrent=config.concurrent, timeout=config.timeout ):
        self.requester = requester( name=self.name, flag=self.flag, timeout=timeout, concurrent=concurrent )
        self.requester.init()
        self.requester.run_with( run_with )
        return self

    def clean_log( self, dir_logs=config.path_data, logs=config.f_log_sc_json,\
        dir_result=config.path_data, result=config.f_result_clean_log_json ):

        # delete old concated result data
        store.rm_file( r'{}/{}'.format( dir_result, result ) )

        c = 1
        for f in glob.glob( r'{}/{}'.format( dir_logs, logs ) ):
            content = rw.read_from_json( f )
            error = []
            if( not val.empty_struct( content ) ):
                if( self.attemp_access ):
                    # create status report
                    report.create_cleaner_report( f, True )
                    # trigger the requester
                    self.requester.input( content ).run()

                    for e in content:
                        if( e[ self.flag ] ): continue # if the URL is marked to be deletable
                        error.append( e )

                    # if no error exists anymore, delete the log file
                    if( not val.empty_struct( error ) ):
                        report.create_cleaner_result_report( f, len( error ) )
                        rw.write_to_log_json( '{}/{}_{}.json'.format( dir_logs, self.name, c ), error )
                    store.rm_file( r"{}".format( f ) )
                else: report.create_cleaner_report( f, False )
            else:
                print( f'''Empty Log file: {str(f)} Deleted!''' )
                store.rm_file( r"{}".format( f ) )
            # pause the program a little bit
            # time.sleep( 1 )
            c += 1

        if( self.attemp_access ):
            # merge the result into a single file
            still_errs = glob.glob( r'{}/{}_*.json'.format( dir_result, self.name ) )
            if( not val.empty_struct( still_errs ) ):
                print( f'''Starting to merge the remain error logs into a single file......''' )
                error = []
                for f in still_errs:
                    content = rw.read_from_json( f )
                    if( not val.empty_struct( content ) ): error += [ e[ 'url' ] for e in content ]
                    # delete the file
                    store.rm_file( r"{}".format( f ) )

                # delete duplicate items
                error = val.list_deduplicated( error )
                commitment = r'{}/{}'.format( path, result )
                print( textwrap.dedent( f'''\
                    Completed!
                    Remaining items:    {len( error )}
                    Commited into file: {commitment}
                ''') )
                # commit to a new log file
                rw.write_to_log_json( commitment, error )

# the main function
if __name__ == '__main__':
    pass