''' README

This class access list of URLs simultaneously using multi-thread.
Required to specify the parsing functions for web-scraping!

Input: list of URLs to be tested on

Return: data file commitments.
'''

from utilsDAWS import config
from utilsDAWS.ops_file import write_to_json
from utilsDAWS.ops_report import report

import threading
import queue
import requests
import os
import pickle
from traceback import format_exc

class scraper():
    ''' multi-threading scraper '''
    def __init__( self, name='scrape', storage=config.path_data,\
        parse_funct=(lambda x: x.text),\
        concurrent=config.concurrent, timeout=config.timeout ):

        self.name = name                # job name, prefix for all data files
        self.parse_funct = parse_funct  # parsing function

        self.job_queue = queue.Queue()  # thread-safe synchronized queue
        self.lock = threading.Lock()    # Lock for synchronized variable r/w
        self.concurrent = concurrent    # num. of threads
        self.timeout = timeout          # timeout for requests
        self.finished = 0               # tracking scraping progress

        self.storage = storage

        self.l_jobs, self.l_tmp = [], []
        # l_jobs: all urls to scrape
        # l_tmp: temporarily holds response object for urls in l_jobs
        self.l_data, self.l_s_errs, self.l_p_errs = [], [], []

        # thread creation
        self._spawn()

    ''' README
    Clear the variables
    '''
    def reset( self ):
        self.finished = 0
        self.l_jobs.clear()
        self.l_data.clear()
        self.l_s_errs.clear()
        self.l_p_errs.clear()
        self.l_tmp.clear()
        return self

    ''' README
    Assign the data input (Type: list).
    Initiate progress tracing variables.
    '''
    def input( self, input ):
        if( not self.l_jobs ): self.l_jobs = input
        elif( self.l_jobs ):   self.l_jobs.extend( input )
        return self

    ''' README
    Assign the name of the task. Simultaneously, the pathes for data commitment are created.
    '''
    def name_with( self, name ):
        ''' consume name and reconfigure paths '''
        self.name = name
        self.path_f_data = os.path.join( self.storage, f'{name}.json' )
        self.path_f_scrape_err = os.path.join( self.storage, f'{name}_scrape_err.json' )
        self.path_f_parse_err = os.path.join( self.storage, f'{name}_parse_err.json' )
        return self

    ''' README
    Assign the parsing function for scraping.
    '''
    def parse_with( self, parse_funct ):
        self.parse_funct = parse_funct
        return self

    ''' README
    Start the process.
    '''
    def run( self ):

        pre = None
        while( self.l_jobs or \
               self.l_s_errs or \
               self.l_p_errs ):

            def create_list( l ): return list(map( lambda x: x[ 'url' ], l ))

            if( len( self.l_s_errs ) ): self.l_jobs.extend( create_list( self.l_s_errs ) )
            if( len( self.l_p_errs ) ): self.l_jobs.extend( create_list( self.l_p_errs ) )

            # items that keep failed!
            if( pre and sorted(self.l_jobs) == pre ):
                self._save()
                report.create_scraper_report( len(self.l_data), \
                                              len(self.l_s_errs), \
                                              len(self.l_p_errs), msg="Some error presented!" )
                self.l_s_errs.clear()
                self.l_p_errs.clear()

                return

            pre = sorted( self.l_jobs )

            self.l_s_errs.clear()
            self.l_p_errs.clear()

            print( f'Scraping started with {len(self.l_jobs)} jobs......' )
            # put the job into job queue
            for url in self.l_jobs: self.job_queue.put(url)
            self.job_queue.join()

            self.l_jobs = []
            self._parse()
            self.l_tmp = []
            self.finished = 0

        self._save()
        report.create_scraper_report( len(self.l_data), \
                                      len(self.l_s_errs), \
                                      len(self.l_p_errs) )

    ''' README
    Commit the results.
    '''
    def _save( self ):
        ''' save final data. l_data, l_s_errs, l_p_errs '''
        write_to_json( self.path_f_data, self.l_data )
        write_to_json( self.path_f_scrape_err, self.l_s_errs )
        write_to_json( self.path_f_parse_err, self.l_p_errs )

    ''' README
    Assign the job for each thread.
    '''
    def _job( self ):
        ''' job for each thread, makes l_tmp '''
        while( True ):
            url = self.job_queue.get()
            try:
                res = requests.get( url, timeout=self.timeout )
                self.lock.acquire()
                self.l_tmp.append(res)
            except Exception as err:
                self.lock.acquire()
                self.l_s_errs.append( { 'url': url, 'err': str(err) } )
            finally:
                self.finished += 1
                print( f'Progress: {100 * self.finished / len(self.l_jobs):.2f}%', end='\r' )
                self.lock.release()
                self.job_queue.task_done()

    ''' README
    Create the threads.
    '''
    def _spawn( self ):
        for _ in range(0, self.concurrent):
            thread = threading.Thread(target=self._job)
            thread.daemon = True
            thread.start()

    ''' README
    Parsing the web source using given parsing funct.
    '''
    def _parse( self ):
        i = 0
        print( '\n' )
        for res in self.l_tmp:
            try:
                data = self.parse_funct(res)
                self.l_data.extend(data)
            except Exception as err:
                self.l_p_errs.append({'url': res.url, 'err': repr(err), 'trace': format_exc() })
            i += 1
            print( f'Parsing..... {i}', end='\r' )
        print( '\nParsing completed!\n' )

''' README

Trigger the scraper class and perform action

Input:
  - name: name of the task
  - in_chunk: whether to perform actions in parts, True/False
  - data: data input
  - parse_funct: parsing funct for scraping
  - start: index for job starting point
  - concurrent: num. of threads
  - partition: size of chunk
  - timeout: timeout for reqests
'''
def trigger_scraper( name='scrape', in_chunk=False,\
    data=[], parse_funct=(lambda x: x.text),
    start=config.start, concurrent=config.concurrent, partition=config.partition, timeout=config.timeout ):

    # make sure the data is in the same order
    data = sorted( data )

    # create the scraper object
    s = scraper( concurrent=concurrent, timeout=timeout )
    if( in_chunk ):
        status = report.reporter()
        for i in range( start, len( data ), partition ):
            if( i > len( data ) ): break

            status.create_progress_report( len( data ), i )

            tail = (i + partition)
            if( tail >= len( data ) ): tail = len( data )

            s.name_with( '{}_{}-{}'.format( name, i, tail ) )
            s.input( data[ i:tail ] ).parse_with( parse_funct ).run()
    # run in whole
    else: s.name_with( name ).input( data ).parse_with( parse_funct ).run()

if __name__ == '__main__':
    pass