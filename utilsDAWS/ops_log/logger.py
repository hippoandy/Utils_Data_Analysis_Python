import logging

__all__ = [ 'logger' ]

class logger():
    def __init__( self, fname='debug.log', mode='w+', log_format='%(name)s - %(levelname)s - %(message)s', level='' ):
        self.fname = fname
        self.mode = mode
        self.format = log_format
        self.level = level

        logging.basicConfig( filename=self.fname, filemode=self.mode, format=self.format )
        if( self.level != '' ):
            try:    logging.basicConfig( level=self.level )
            except: logging.error( 'No such level available! Not changing the loggin level.' )

    def set_fname( self, fname ):
        self.fname = fname
        logging.basicConfig( filename=self.fname )
        return self

    def set_fmode( self, mode ):
        self.mode = mode
        logging.basicConfig( mode=self.mode )
        return self

    def set_format( self, format ):
        self.format = format
        logging.basicConfig( format=self.format )
        return self

    def commit( self, type="", msg="Something bad happened!" ):
        if( type == 'error' ):      logging.error( msg )
        elif( type == 'warning' ):  logging.warning( msg )
        elif( type == 'debug' ):    logging.debug( msg )
        elif( type == 'except' ):   logging.exception( msg )
        else:                       logging.error( msg )
    