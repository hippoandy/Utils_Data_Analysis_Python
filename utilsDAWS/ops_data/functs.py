import re



__all__ = [
    'find_numeric',
    'empty_struct',
    'invalid_val',
    'basic_cleaning',
    'clean_str', 'clean_num',
    'clear_multi_text',
    'clear_char', 'clear_dot', 'clear_comma',
    'comma_to_hyphen',
    'is_numeric', 'numeric', 'make_numeric',
]

# find the numeric value within a string
def find_numeric( text ):
    if( text == invalid_val() ): return invalid_val()
    try:    return re.findall( r'\d+', text )[ 0 ]
    # try:    return re.search( r'\d+', text ).group( 0 )
    except: return invalid_val()
# check if struct is_empty
def empty_struct( struct ):
    if struct: return False
    else: return True
def invalid_val(): return 'N/A'
# the basic cleaning that applies to all the value
def basic_cleaning( text ):
    return clean_str( clear_comma( text ) )
# make sure there is no special char in a value
def clean_str( text ):
    return str(text).replace( '\n', '' ).replace( '\r', '' ).replace( '\t', '' )
# remove ',' and '.' from numeric values
def clean_num( text ):
    return clear_dot( clear_comma( text ) )
def clear_multi_text( text, l=[] ):
    for e in l: text = text.replace( e, '' )
    return text
# clear the char in the string tar
def clear_char( text, tar ):
    for t in tar: text = text.replace( t, '' )
    return text
def clear_dot( text ):
    return str(text).replace( '.', '' )
# clear ',' in the value
def clear_comma( text ):
    return str(text).replace( ',', '' )
# replace ',' with '-'
def comma_to_hyphen( text ):
    return str(text).replace( ',', '-' )
def is_numeric( val, type='float' ):
    val = str(val) # make sure it is not 'NoneType'
    try: # make sure the value is numeric
        if( type == 'int' ): val = int(val)
        else: val = float(val)
        return True
    except: return False
# make sure the value is numeric, otherwise return invalid_val()
def numeric( val, type='float' ):
    if( is_numeric( val, type ) ): return str(val)
    else: return invalid_val()
# create numerical value
def make_numeric( text, type='float' ):
    if( text != invalid_val() ):
        if( type == 'int' ): return int(text)
        else: return float(text)
    else: return invalid_val()