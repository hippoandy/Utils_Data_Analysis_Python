import re
import textwrap
import pandas as pd

__all__ = [
    'is_api_success', 'api_json_available',
    'find_numeric', 'find_all_numeric',
    'get_unit',
    'empty_struct',
    'invalid_val',
    'basic_cleaning',
    'clean_str', 'clean_num',
    'clear_multi_text',
    'clear_char', 'clear_dot', 'clear_comma',
    'comma_to_hyphen',
    'is_numeric', 'numeric', 'make_numeric',
    'url_country_domain',
    'list_deduplicated',
]

def is_api_success( r ):
    if( r != None and r.status_code == 200 ): return True
    else: return False

def api_json_available( r ):
    try: return not empty_struct( r.json() )
    except: return False

# find country domain in url
''' README

Return value format: two digit country domain
ex. 'ar', 'bo', 'cl'
'''
def url_country_domain( url ):
    try:    domain = re.findall( r"\b" + r'\.[a-z]{2}\/' + r"\b", str(url) )[ 0 ]
    except: domain = re.findall( r'\.[a-z]{2}\/', str(url) )[ 0 ]
    domain = clear_char( domain, "./" )
    return domain

# find the numeric value within a string
def find_numeric( text ):
    if( text == invalid_val() ): return invalid_val()
    try:    return re.findall( r'\d+', text )[ 0 ]
    # try:    return re.search( r'\d+', text ).group( 0 )
    except: return invalid_val()

def find_all_numeric( text ):
    if( text == invalid_val() ): return invalid_val()
    try:    return re.findall( r'\d+', text )
    # try:    return re.search( r'\d+', exp ).group( 0 )
    except: return []

# get the unit associate with a number
def get_unit( text ):
    try:    return re.sub( r'\d+', ' ', text ).replace( ' ', '' )
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

def list_deduplicated( list_ ):
    df = pd.DataFrame.from_records( { 'item': list_ } )
    df = df.drop_duplicates()
    return df[ 'item' ].tolist()