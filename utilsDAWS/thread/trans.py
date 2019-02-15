''' README

Translate group of text with multithreading using googletrans lib.

Lib. dependency: googletrans

* Please be advised that the API has limited access and will trigger exception if the limit is exceeded!

Retrun the data inplace.

'''

from googletrans import Translator

import threading
import queue
from traceback import format_exc

__all__ = [ 'translator' ]

# self-defined classes ---------------------------------------------
class translator():
    # constructor
    def __init__( self, name='trans', concurrent=30, src="es", dest="en" ):
        self.name = name
        self.concurrent = concurrent
        self.src = src
        self.dest = dest
        self.text_list = []
        self.job_queue = queue.Queue()
        self.lock = threading.Lock()
        self._spawn()
    # set the data to be parsed
    def input( self, text_list ):
        if( not self.text_list ): self.text_list = text_list
        return self
    # ignitiate the thread
    def run( self ):
        for text in self.text_list: self.job_queue.put( text )
        self.job_queue.join()
    # things for the thread to do
    def _job( self ):
        while True:
            obj = self.job_queue.get()
            try:
                translator = Translator()
                obj[ 'translated' ] = translator.translate( str(obj[ 'original' ]), src=self.src, dest=self.dest ).text
                self.lock.acquire()
            except Exception as err:
                print( str(err) )
                self.lock.acquire()
            finally:
                self.lock.release()
                self.job_queue.task_done()
    # creating the threads
    def _spawn( self ):
        for _ in range( 0, self.concurrent ):
            t = threading.Thread( target=self._job )
            t.daemon = True
            t.start()
# --------------------------------------------- self-defined classes