import requests
import textwrap

__all__ = [
    'send_req',
]

''' send a url request '''
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