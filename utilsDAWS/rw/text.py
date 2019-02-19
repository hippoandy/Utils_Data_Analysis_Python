
__all__ = [
    'write_to_text',
    'write_to_log_text'
]

def write_to_text( path, data, encode='utf-8' ):
    f = open( path, 'w+', encoding=encode )
    f.write( data )
    f.close()

# write log in plain text to a file
def write_to_log_text( path, data, encode='utf-8' ):
    write_to_text( path, data, encode=encode )

if __name__ == '__main__':
    pass