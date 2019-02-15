''' README

This class access list of URLs simultaneously using multi-thread.
Try to access the given URLs and see if they are valid.

Input: list of URLsto be tested on

Return the data inplace.
'''

from utilsDAWS.stdout import report

import threading
import queue

import requests
from traceback import format_exc

# general settings --------------------
msg_title = '[retryer]'
# -------------------- general settings

__all__ = [ 'retryer' ]

# self-defined classes ---------------------------------------------
class retryer():
    # constructor
    def __init__( self, name='req', flag='deletable', timeout=10, concurrent=30 ):
        self.name = name
        self.flag = flag
        self.timeout = timeout
        self.concurrent = concurrent
        self.run_funct = None
        self.obj_list = []
        self.job_queue = queue.Queue()
        self.lock = threading.Lock()
        self.finished = 0
        self._spawn()

    ''' clear temp storages and parameters used by this class '''
    def init( self ):
        self.obj_list = []
        self.finished = 0

    ''' set the function to parse accessed url content '''
    def run_with( self, funct ):
        self.run_funct = funct
        return self

    ''' set the data to be accesed '''
    def input( self, obj_list ):
        self.init()
        self.obj_list = obj_list
        return self

    ''' ignitiate the thread '''
    def run( self ):
        print( f'''{msg_title} Number of URLs to retry: {len( self.obj_list )}''')
        for obj in self.obj_list: self.job_queue.put( obj )
        self.job_queue.join()
        print( f'''{msg_title} Operations finished!''' )

    ''' things for the thread to do '''
    def _job( self ):
        while True:
            obj = self.job_queue.get()
            try:
                obj[ self.flag ] = False
                try:
                    r = requests.get( obj[ 'url' ], timeout=self.timeout ) # get web code
                    # the parse funct will return if the page is exist
                    # if the page exist, then NOT deletable
                    if( r != None and self.run_funct != None ): obj[ self.flag ] = (not self.run_funct( r ))
                    else: obj[ self.flag ] = False
                except requests.exceptions.ConnectionError:
                    obj[ self.flag ] = True
                except Exception as err: pass
                self.lock.acquire()
            except Exception as err:
                print( str(err) )
                self.lock.acquire()
            finally:
                self.finished += 1
                report.general_progress( self.finished, len( self.obj_list ) )
                self.lock.release()
                self.job_queue.task_done()

    ''' creating the threads '''
    def _spawn( self ):
        for _ in range( 0, self.concurrent ):
            t = threading.Thread( target=self._job )
            t.daemon = True
            t.start()
# --------------------------------------------- self-defined classes