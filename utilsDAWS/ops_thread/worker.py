

import threading
import queue

import textwrap
from traceback import format_exc

import config
from utils import ops_file as rw

__all__ = [ 'worker' ]

# self-defined classes ---------------------------------------------
class worker():
    # constructor
    def __init__( self, name='worker', timeout=10, concurrent=10, result_to_file=False ):
        self.name = name
        self.ext = ''
        self.data_path = r'{}/{}'.format( config.path_data, name )
        self.out_header = ''

        self.timeout = timeout
        self.concurrent = concurrent
        self.parse_funct = None
        self.result_to_file = result_to_file

        self.data_list = []
        self.obj_list = []
        self.job_queue = queue.Queue()
        self.lock = threading.Lock()
        self.finished = 0
        self._spawn()

    def init( self ):
        self.data_list = []
        self.obj_list = []
        self.finished = 0

    def name_with( self, name ):
        self.name = name
        return self

    def work_with( self, funct ):
        self.parse_funct = funct
        return self

    ''' set the data to be parsed '''
    def input( self, obj_list ):
        self.obj_list = obj_list
        return self

    ''' set the output file path, name, and extension '''
    def output( self, name, ext ):
        self.name = name
        self.ext = ext
        self.data_path = r'{}/{}.{}'.format( config.path_data, self.name, self.ext )
        return self

    ''' set the output file header if needed '''
    def output_header( self, header ):
        self.out_header = header
        return self

    ''' ignitiate '''
    def run( self ):
        print( textwrap.dedent( f'''
            Worker initiated! Number of items: {len( self.obj_list )}
        ''') )
        for obj in self.obj_list: self.job_queue.put( obj )
        self.job_queue.join()

        if( self.result_to_file ): 
            # commit the results
            rw.list_to_csv( self.data_path, self.data_list, header=self.out_header )
        print( 'finished!' )

    ''' things for the thread to do '''
    def _job( self ):
        while True:
            obj = self.job_queue.get()
            try:
                if( self.result_to_file ): self.data_list.extend( self.parse_funct( obj ) )
                else: self.parse_funct( obj )
                self.lock.acquire()
            except Exception as err:
                print( str(err) )
                self.lock.acquire()
            finally:
                self.finished += 1
                print(f'process: {100 * self.finished / len(self.obj_list):.2f}%', end='\r')
                self.lock.release()
                self.job_queue.task_done()

    ''' creating the threads '''
    def _spawn( self ):
        for _ in range( 0, self.concurrent ):
            t = threading.Thread( target=self._job )
            t.daemon = True
            t.start()
# --------------------------------------------- self-defined classes