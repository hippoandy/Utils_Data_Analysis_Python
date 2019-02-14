import time
import textwrap

__all__ = [
    'reporter',
    'create_scraper_report'
]

class reporter():
    def __init__( self ):
        self.t_start = time.time()
        self.p_start = None        # record start poing

    ''' README

    Create progress report for iteration.

    Input:
      - num_job: total num. of jobs
      - current: index for current progress
      - t_start: program start time
    '''
    def create_progress_report( self, num_job, current ):
        if( self.p_start == None ): self.p_start = current
        total = (num_job - current)
        completed = (current - self.p_start)

        print( textwrap.dedent( f'''\
            ----------------------------------------------------------
            Status Report:
                Total jobs:     {total}
                Completed jobs: {completed}
                Remaining jobs: {total - completed}
                Percentage:     {100 * completed / total:.2f} (%)
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