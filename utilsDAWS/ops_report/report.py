import time
import textwrap

__all__ = [
    'reporter',
    'create_scraper_report'
]

class reporter():
    def __init__( self ):
        self.t_start = time.time()

    ''' README

    Create progress report for iteration.

    Input:
      - num_job: total num. of jobs
      - current: index for current progress
      - t_start: program start time
    '''
    def create_progress_report( self, num_job, current ):
        print( textwrap.dedent( f'''\
            Status Report:
                Remaining jobs: {num_job - current}
                Percentage:     {100 * current / num_job:.2f} %
                Executed for    {time.time() - self.t_start} seconds
        ''' ) )

def create_scraper_report( len_data, len_scrape_err, len_parse_err, msg="Finished" ):
    print(textwrap.dedent(f'''\
        {msg}:
            Num. of data completed: {len_data}
            Num. of scraping error: {len_scrape_err}
            Num. of parsing error:  {len_parse_err}
    '''))