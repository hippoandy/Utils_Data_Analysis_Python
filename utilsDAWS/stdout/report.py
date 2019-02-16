import time
import textwrap

__all__ = [
    'reporter',
    'create_scraper_report',
    'create_cleaner_report',
    'create_cleaner_attempt_report'
]

class reporter():
    def __init__( self ):
        self.t_start = time.time()  # program start time

    ''' README

    Create progress report for iteration.

    Input:
        - num_job: total num. of jobs
        - current: index for current progress
        - t_start: program start time
    '''
    def create_progress_report( self, num_job, current ):
        print( textwrap.dedent( f'''\
            ----------------------------------------------------------
            Status Report:
                Total jobs:     {num_job}
                Completed jobs: {current}
                Remaining jobs: {num_job - current}
                Percentage:     {100 * current / num_job:.2f} (%)
                Executed for    {time.time() - self.t_start:.2f} (sec)
            ----------------------------------------------------------
        ''' ) )

''' README

Create status report for scraper class.

Input:
    - len_data: total num. of data saved
    - len_scrape_err: num. of job failed due to scraping error
    - len_parse_err:  num. of job failed due to parsing error
    - msg: custom message
'''
def create_scraper_report( len_data, len_scrape_err, len_parse_err, msg="Finished" ):
    print(textwrap.dedent(f'''\
        {msg}:
            Num. of data completed: {len_data}
            Num. of scraping error: {len_scrape_err}
            Num. of parsing error:  {len_parse_err}
    '''))

''' README

Create status report for cleaner class.

Input:
    - msg_title: title
    - len_remaining: len. of remaing items
    - f_result: filename
'''
def create_cleaner_report( msg_title, len_remaining, f_result ):
    print( textwrap.dedent( f'''\
        {msg_title} Completed!
            Remaining items:    {len_remaining}
            Commited into file: {f_result}
    ''') )


''' README

Create result report for cleaner class.

Input:
    - f_log: filename
    - len_result: len of the result data
'''
def create_cleaner_attempt_report( f_log, len_result ):
    print( textwrap.dedent( f'''\
        \n
        --------------------------------------------------
        Still have items that not able to be removed......
            Num. of remaining items: {len_result}
            File: {f_log} completed
        --------------------------------------------------
        \n
    ''') )