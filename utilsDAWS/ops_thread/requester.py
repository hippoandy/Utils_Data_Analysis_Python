import threading
import queue

import requests
import textwrap
from traceback import format_exc

__all__ = [ 'requester' ]

# self-defined classes ---------------------------------------------

# access group of urls with multithreading
''' README

This class is used for error log check.
Try to re-access the URLs and see if they are valid.

Input: the error log file named in:
  - "*_scrape_err.json"
  - "*_parse_err.json"

Return the data inplace.

'''
class requester():
    # constructor
    def __init__( self, name='req', res_key='deletable', timeout=10, concurrent=30 ):
        self.name = name
        self.res_key = res_key
        self.timeout = timeout
        self.concurrent = concurrent
        self.parse_funct = None
        self.obj_list = []
        self.job_queue = queue.Queue()
        self.lock = threading.Lock()
        self.finished = 0
        self._spawn()

    def init( self ):
        self.obj_list = []
        self.finished = 0

    def parse_with( self, funct ):
        self.parse_funct = funct
        return self
    # set the data to be parsed
    def input( self, obj_list ):
        if( not self.obj_list ): self.obj_list = obj_list
        return self
    # ignitiate the thread
    def run( self ):
        print( textwrap.dedent( f'''
            Revisiting the URLs......
                Number of URLs: {len( self.obj_list )}
        ''') )
        for obj in self.obj_list: self.job_queue.put( obj )
        self.job_queue.join()
        print( 'finished!' )
    # things for the thread to do
    def _job( self ):
        while True:
            obj = self.job_queue.get()
            try:
                obj[ self.res_key ] = False
                # r = send_req( obj[ 'url' ], self.timeout, '' )
                try:
                    r = requests.get( obj[ 'url' ], timeout=self.timeout ) # get web code
                    # the parse funct will return if the page is exist
                    # if the page exist, then NOT deletable
                    if( r != None ): obj[ self.res_key ] = (not self.parse_funct( r ))
                except requests.exceptions.ConnectionError:
                    obj[ self.res_key ] = True
                except Exception as err: pass
                self.lock.acquire()
            except Exception as err:
                print( str(err) )
                self.lock.acquire()
            finally:
                self.finished += 1
                print(f'process: {100 * self.finished / len(self.obj_list):.2f}%', end='\r')
                self.lock.release()
                self.job_queue.task_done()
    # creating the threads
    def _spawn( self ):
        for _ in range( 0, self.concurrent ):
            t = threading.Thread( target=self._job )
            t.daemon = True
            t.start()
# --------------------------------------------- self-defined classes