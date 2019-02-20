''' README

This class work on a given task for a group of objects.

Input: list of objects to be worked on

Return:
  - the data inplace, or
  - a file output
'''
from utilsDAWS import config
from utilsDAWS import rw
from utilsDAWS.stdout import report, stdout

import threading
import queue

import textwrap
from traceback import format_exc

# general settings --------------------
msg_title = '[worker]'
# -------------------- general settings

__all__ = [ 'worker', 'trigger_worker' ]

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
        self.work_funct = None
        self.result_to_file = result_to_file

        self.data_list = []
        self.obj_list = []
        self.job_queue = queue.Queue()
        self.lock = threading.Lock()
        self.finished = 0
        self._spawn()

    ''' clear temp storages and parameters used by this class '''
    def reset( self ):
        self.data_list = []
        self.obj_list = []
        self.finished = 0

    ''' determine the name of the job '''
    def name_with( self, name ):
        self.name = name
        return self

    ''' setting the working function '''
    def work_with( self, funct ):
        self.work_funct = funct
        return self

    ''' set the data to be parsed '''
    def input( self, obj_list ):
        self.reset()
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
        print( f'''{msg_title} Number of items: {len( self.obj_list )}''')
        for obj in self.obj_list: self.job_queue.put( obj )
        self.job_queue.join()

        if( self.result_to_file ): 
            # commit the results
            rw.list_to_csv( self.data_path, self.data_list, header=self.out_header )
        print( f'''{msg_title} Operations finished!''' )

    ''' things for the thread to do '''
    def _job( self ):
        while True:
            obj = self.job_queue.get()
            try:
                if( self.result_to_file ): self.data_list.extend( self.work_funct( obj ) )
                else: self.work_funct( obj )
                self.lock.acquire()
            except Exception as err:
                print( str(err) )
                self.lock.acquire()
            finally:
                self.finished += 1
                stdout.general_progress( self.finished, len( self.obj_list ), msg_title )
                self.lock.release()
                self.job_queue.task_done()

    ''' creating the threads '''
    def _spawn( self ):
        for _ in range( 0, self.concurrent ):
            t = threading.Thread( target=self._job )
            t.daemon = True
            t.start()
# --------------------------------------------- self-defined classes

## TO-DO
''' README

Trigger the worker class and perform action

Input:
  - name: name of the task
  - in_chunk: whether to perform actions in parts, True/False
  - data: data input
  - work_funct: parsing funct for scraping
  - start: index for job starting point
  - concurrent: num. of threads
  - partition: size of chunk
  - timeout: timeout for reqests
'''
def trigger_worker( name='work', in_chunk=False,\
    data=[], work_funct=(lambda x: x.text), result_to_file=False,\
    output_header='', output_name='', output_type='', 
    start=config.start, concurrent=config.concurrent, partition=config.partition, timeout=config.timeout ):

    # make sure the data is in the same order
    data = sorted( data )

    # create worker class
    w = worker( name=name, concurrent=concurrent, timeout=timeout, result_to_file=result_to_file )
    if( in_chunk ):
        status = report.reporter()
        for i in range( 0, len(data), partition ):
            if( i > len( data) ): break

            status.create_progress_report( len( data ), i )

            tail = (i + partition)
            if( tail >= len(data) ): tail = len(data)
            # run by multi-threaded worker
            w.input( data[ i:tail ] )
            
            if( result_to_file ):
                w.output( '{}_{}-{}'.format( output_name, i, tail ), output_type ).output_header( output_header )

            w.work_with( work_funct ).run()

    # run in whole
    else:
        w.input( data )

        if( result_to_file ):
            w.output( '{}'.format( output_name ), output_type ).output_header( output_header )

        w.work_with( work_funct ).run()

if __name__ == '__main__':
    pass