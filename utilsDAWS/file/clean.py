from utilsDAWS import config
from utilsDAWS import value as val
from utilsDAWS.request import retry
from utilsDAWS import rw
from utilsDAWS import file
from utilsDAWS.stdout import report

import glob
import argparse

# general settings --------------------
msg_title = '[clean_log]'
# -------------------- general settings

__all__ = [
    'clean_log'
]

''' README

Cleaning empty log files created by the scraper

'''
def clean_log( attemp_access=False, name=config.n_scrape_clean, \
    dir_logs=config.path_data, logs=config.f_log_sc_json,\
    dir_result=config.path_data, result=config.f_result_clean_log_json, \
    run_with=None, flag='deletable', \
    concurrent=config.concurrent, timeout=config.timeout ):

    # delete old concated result data
    file.rm_file( r'{}/{}'.format( dir_result, result ) )

    # if user wish to retry access, init the retryer class
    if( attemp_access ):
        retryer = retry.retryer( name=name, flag=flag, timeout=timeout, concurrent=concurrent )
        retryer.init()
        retryer.run_with( run_with )

    c = 1
    for f in glob.glob( r'{}/{}'.format( dir_logs, logs ) ):
        content = rw.read_from_json( f )
        error = []
        if( not val.empty_struct( content ) ):
            print( f'''{msg_title} Non-empty Log file: {str(f)}''' )
            if( attemp_access ):
                print( f'''{msg_title} Attempt to retry......''')
                # trigger the retryer
                retryer.input( content ).run()

                for e in content:
                    if( e[ flag ] ): continue # if the URL is marked to be deletable
                    error.append( e )

                # if no error exists anymore, delete the log file
                if( not val.empty_struct( error ) ):
                    report.create_cleaner_attempt_report( f, len( error ) )
                    rw.write_to_log_json( '{}/{}_{}.json'.format( dir_logs, name, c ), error )
                file.rm_file( r"{}".format( f ) )
            else:
                print( f'''{msg_title} Not attempt to retry, keep the file instead......''')
        else:
            print( f'''{msg_title} Deleted empty Log file: {str(f)}''' )
            file.rm_file( r"{}".format( f ) )
        c += 1

    if( attemp_access ):
        # merge the result into a single file
        still_errs = glob.glob( r'{}/{}_*.json'.format( dir_result, name ) )
        if( not val.empty_struct( still_errs ) ):
            print( f'''{msg_title} Merging the error logs into a single file......''' )
            error = []
            for f in still_errs:
                content = rw.read_from_json( f )
                if( not val.empty_struct( content ) ): error += [ e[ 'url' ] for e in content ]
                # delete the file
                file.rm_file( r"{}".format( f ) )

            # delete duplicate items
            error = val.list_deduplicated( error )
            commitment = r'{}/{}'.format( dir_result, result )
            report.create_cleaner_report( msg_title, len( error ), commitment )
            # commit to a new log file
            rw.write_to_log_json( commitment, error )

# the main function
if __name__ == '__main__':
    pass