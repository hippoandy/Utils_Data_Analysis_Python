from utilsDAWS import value as val

import requests
import textwrap

__all__ = [
    'error_403', 'error_404',
    'is_api_success', 'api_json_available',
    'send_req',
]


def error_403( status_code ):
    if( status_code == 403 ):   return True
    else:                       return False

def error_404( status_code ):
    if( status_code == 404 ):   return True
    else:                       return False

''' README

Test if the given API link is accessible.

Retrun: boolean
'''
def is_api_success( r ):
    if( r != None and r.status_code == 200 ): return True
    else: return False

''' README

Test if JSON format data availabe in given response.

Retrun: boolean
'''
def api_json_available( r ):
    try: return not val.empty_struct( r.json() )
    except: return False

''' README
Send an URL request.
 '''
def send_req( url, timeout=10, err_msg="" ):
    try:
        r = requests.get( url, timeout=timeout ) # get web code
    except Exception as e:
        # print( textwrap.dedent( f'''
        #     Error while accessing the url: {url}
        #         Error Msg: {repr(e)}
        #         Trace: {format_exc()}
        # '''))
        print( textwrap.dedent( f'''
            Error while accessing the url: {url}
                Error Msg: {repr(e)}
        '''))
        return None
    # if( r.status_code != 200 ):
    #     print( textwrap.dedent( f'''
    #         Unable to access the url: {url}
    #             Status Code: {r.status_code}
    #             Error Msg: {err_msg}
    #     '''))
    #     return r
    return r