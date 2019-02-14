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
        parse_func=(lambda x: x.text),\
        concurrent=config.concurrent, timeout=config.timeout ):
        '''
            name: job name, prefix for all data files
            list_job: all urls to scrape
            list_tmp: temporarily holds response object for urls in list_job
            parse_func: parsing function, provided by user

            storage: storage directory for all data
            path_f_data: path for data
            path_f_scrape_err: path for scrape errors
            path_f_parse_err: path for parse errors

            job_queue: thread-safe synchronized queue
            lock: Lock for synchronized variable read/write
            concurrent: number of threads
            timeout: timeout for each request
            finished: tracking scraping progress

            list_data: final data, after scraping, all data should be here
            list_scrape_err: scrape errors, [{'url': <failed url>, 'err': <error msg>}]
            list_parse_err: parsing errors, [{'url': <failed url>, 'err': <error msg>}]
        '''
        self.name = name
        self.parse_func = parse_func

        self.job_queue = queue.Queue()
        self.lock = threading.Lock()
        self.concurrent = concurrent
        self.timeout = timeout
        self.finished = 0

        self.storage = storage

        self.list_job, self.list_tmp = [], []
        self.list_data, self.list_scrape_err, self.list_parse_err, self.list_tmp = [], [], [], []

        self._spawn_threads()

    def reset( self ):
        ''' reset all results, clean for another run '''
        self.finished = 0
        self.list_job.clear()
        self.list_data.clear()
        self.list_scrape_err.clear()
        self.list_parse_err.clear()
        self.list_tmp.clear()
        return self

    def input( self, input ):
        ''' consume url list passed by user '''
        if( not self.list_job ): self.list_job = input
        elif( self.list_job ):   self.list_job.extend( input )
        return self

    def name_with( self, name ):
        ''' consume name and reconfigure paths '''
        self.name = name
        self.path_f_data = os.path.join( self.storage, f'{name}.json' )
        self.path_f_scrape_err = os.path.join( self.storage, f'{name}_scrape_err.json' )
        self.path_f_parse_err = os.path.join( self.storage, f'{name}_parse_err.json' )
        return self

    def parse_with( self, parse_func ):
        ''' comsume parsing function passed by user '''
        self.parse_func = parse_func
        return self

    def run_once(self):
        ''' run once '''
        pass

    def run_until_done(self):
        ''' run until no list_scrape_err or list_parse_err or stuck '''
        pre_url_lst_sorted = None
        while self.list_job or self.list_scrape_err or self.list_parse_err:
            if( self.list_scrape_err ):
                self.list_job.extend( list(map(lambda x: x['url'], self.list_scrape_err)) )

            if( self.list_parse_err ):
                self.list_job.extend( list(map(lambda x: x['url'], self.list_parse_err)) )

            # items that keep failed!
            if( pre_url_lst_sorted and sorted(self.list_job) == pre_url_lst_sorted ):
                self._save()
                report.create_scraper_report( len(self.list_data), len(self.list_scrape_err), len(self.list_parse_err), msg="Some error presented!" )
                self.list_scrape_err.clear()
                self.list_parse_err.clear()

                return

            pre_url_lst_sorted = sorted( self.list_job )

            self.list_scrape_err.clear()
            self.list_parse_err.clear()

            print( f'Scraping started with {len(self.list_job)} jobs......' )
            for url in self.list_job: self.job_queue.put(url)

            self.job_queue.join()
            self.list_job = []
            self._parse()
            self.list_tmp = []
            self.finished = 0

        self._save()
        report.create_scraper_report( len(self.list_data), len(self.list_scrape_err), len(self.list_parse_err) )

    def _save( self ):
        ''' save final data. list_data, list_scrape_err, list_parse_err '''
        write_to_json( self.path_f_data, self.list_data )
        write_to_json( self.path_f_scrape_err, self.list_scrape_err )
        write_to_json( self.path_f_parse_err, self.list_parse_err )

    def _job( self ):
        ''' job for each thread, makes list_tmp '''
        while( True ):
            url = self.job_queue.get()
            try:
                res = requests.get( url, timeout=self.timeout )
                self.lock.acquire()
                self.list_tmp.append(res)
            except Exception as err:
                self.lock.acquire()
                self.list_scrape_err.append( { 'url': url, 'err': str(err) } )
            finally:
                self.finished += 1
                print(f'Progress: {100 * self.finished / len(self.list_job):.2f}%', end='\r')
                self.lock.release()
                self.job_queue.task_done()

    def _spawn_threads( self ):
        ''' start threads as daemons '''
        for _ in range(0, self.concurrent):
            thread = threading.Thread(target=self._job)
            thread.daemon = True
            thread.start()

    def _parse( self ):
        ''' parse res using parse_func '''
        i = 0
        print( '\n' )
        for res in self.list_tmp:
            try:
                data = self.parse_func(res)
                self.list_data.extend(data)
            except Exception as err:
                self.list_parse_err.append({'url': res.url, 'err': repr(err), 'trace': format_exc() })
            i += 1
            print( f'Parsing..... {i}', end='\r' )
        print( '\nParsing completed!\n' )

''' README

Trigger the scraper class and perform action

Input:
  - in_chunk: whether to perform actions in parts, True/False

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

            s.reset().name_with( '{}_{}-{}'.format( name, i, tail ) )
            s.input( data[ i:tail ] ).parse_with( parse_funct ).run_until_done()
    # run in whole
    else: s.reset().name_with( name ).input( data ).parse_with( parse_funct ).run_until_done()

if __name__ == '__main__':
    pass