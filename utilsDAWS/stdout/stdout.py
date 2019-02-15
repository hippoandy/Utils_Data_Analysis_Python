__all__ = [
    'general_progress'
]

''' README

General progress STDOUT

Input:
    - completed: num. of job completed
    - total: num. of total jobs
'''
def general_progress( completed, total, msg_title='' ):
    if( msg_title != '' ):
        print( f'''{msg_title} Process: {100 * completed / total:.2f}%''', end='\r' )
    else:    
        print( f'''Process: {100 * completed / total:.2f}%''', end='\r' )