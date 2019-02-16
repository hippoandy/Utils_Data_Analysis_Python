''' README

This class access list of URLs simultaneously using multi-thread.
Required to specify the parsing functions for web-scraping!

Input: list of URLs to be tested on

Return: data file commitments.
'''

from utilsDAWS import config
from utilsDAWS import value as val
from utilsDAWS.file import clean
from utilsDAWS.file import file
from utilsDAWS import rw
from utilsDAWS.stdout import report, stdout

import time
import threading
import queue
import requests
import os
import pickle
from traceback import format_exc

# general settings --------------------
msg_title = '[scraper]'
# -------------------- general settings

__all__ = [
    'scraper',
    'trigger_scraper',
    'run_with_retry',
]

# self-defined classes ---------------------------------------------
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

    ''' README
    Assign the data input (Type: list).
    Initiate progress tracing variables.
    '''
    def input( self, input ):
        self.reset()
        self.l_jobs = input
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
                                              len(self.l_p_errs), msg="{} Encountered errors".format( msg_title ) )
                return

            pre = sorted( self.l_jobs )
            self.l_s_errs.clear()
            self.l_p_errs.clear()

            print( f'''{msg_title} Scraping started with {len(self.l_jobs)} jobs......''' )
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
                                      len(self.l_p_errs), msg='{} finished'.format( msg_title ) )

    ''' README
    Commit the results.
    '''
    def _save( self ):
        ''' save final data. l_data, l_s_errs, l_p_errs '''
        rw.write_to_json( self.path_f_data, self.l_data )
        rw.write_to_json( self.path_f_scrape_err, self.l_s_errs )
        rw.write_to_json( self.path_f_parse_err, self.l_p_errs )

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
                stdout.general_progress( self.finished, len( self.l_jobs ), msg_title )
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
            print( f'''{msg_title} Parsing..... {i}''', end='\r' )
        print( f'''\n{msg_title} Parsing completed!\n''' )
# --------------------------------------------- self-defined classes

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

''' README

Trigger the scraper class and perform action.
This funct. will also clear the error log and perform retrial.

Input:
    - data: data input
    - name: name of the data files
    - name_retry: name of retry files
    - parse_funct: parsing funct for scraping
    - attemp_acc_funct: funct for retrial
    - start: index start poing
    - concurrent: num. of threads
    - partition: size of chunk
    - timeout: timeout for reqests
'''
def run_with_retry( data, name, name_retry,
    parse_funct, attemp_acc_funct, start, concurrent, partition, timeout, encode ):

    n_scraper = name
    start = start

    pre = []
    retried = 0
    while( True ):
        if( len( pre ) ): data = pre

        trigger_scraper( name=n_scraper, in_chunk=True,\
            data=data, parse_funct=parse_funct,\
            start=start, concurrent=concurrent, partition=partition, timeout=timeout )

        time.sleep( config.sleep_med )

        # clear the log
        clean.clean_log( name='clear_log_{}'.format( name ), dir_logs=config.path_data, logs='{}*_err.json'.format( name ),\
            dir_result=config.path_data, result='{}_to-retry.json'.format( name_retry ), \
            attemp_access=True, \
            run_with=attemp_acc_funct, concurrent=concurrent, timeout=timeout )

        try:    to_retry = rw.read_from_json( r'{}/{}'.format( config.path_data, '{}_to-retry.json'.format( name_retry ) ) )
        except: to_retry = []

        if( val.empty_struct( to_retry ) ):
            file.rm_file( '{}_to-retry.json'.format( name_retry ) )
            break

        if( sorted( to_retry ) == pre ):
            file.rm_file( '{}_to-retry.json'.format( name_retry ) )
            print( f'''{len( to_retry )} URLs failed to scrape!''' )
            rw.write_to_json( r'{}/{}'.format( config.path_data, '{}_failed.json'.format( name_retry ) ), to_retry )
            break

        pre = sorted( to_retry )
        start = 0                   # important!!!
        retried += 1
        n_scraper = '{}_retry_{}'.format( name, retried )

    # concate
    rw.concat_json_files( dir_files=config.path_data, files=r'{}_*json'.format( name ), \
        dir_result=config.path_data, result=r'{}.json'.format( name ), encode=encode, del_empty=True )

if __name__ == '__main__':
    pass