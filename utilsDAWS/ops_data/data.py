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

''' README

Test if the given API link is accessible.

Retrun: boolean
'''
def is_api_success( r ):
    if( r != None and r.status_code == 200 ): return True
    else: return False

def api_json_available( r ):
    try: return not empty_struct( r.json() )
    except: return False

''' README

Find country domain in the given URL.

Return: two digit country domain
  - ex. 'ar', 'bo', 'cl'
'''
def url_country_domain( url ):
    try:    domain = re.findall( r"\b" + r'\.[a-z]{2}\/' + r"\b", str(url) )[ 0 ]
    except: domain = re.findall( r'\.[a-z]{2}\/', str(url) )[ 0 ]
    domain = clear_char( domain, "./" )
    return domain

''' README

Find the numeric value within a string.

Return: the numeric value founded
'''
def find_numeric( text ):
    if( text == invalid_val() ): return invalid_val()
    try:    return re.findall( r'\d+', text )[ 0 ]
    # try:    return re.search( r'\d+', text ).group( 0 )
    except: return invalid_val()

''' README

Find all the numeric values within a string.

Return: list of the numeric values founded
'''
def find_all_numeric( text ):
    if( text == invalid_val() ): return invalid_val()
    try:    return re.findall( r'\d+', text )
    # try:    return re.search( r'\d+', exp ).group( 0 )
    except: return []

''' README

Get the unit associate with a number.

Input: a numberassociate with a string, for example: '1 liter'

Return: the text been found
  - for example:
      input:    '1 liter'
      return:   'liter'
'''
def get_unit( text ):
    try:    return re.sub( r'\d+', ' ', text ).lstrip( ' ' )
    except: return invalid_val()

''' README

Check if the given struct (list, dict) is empty.

Return: boolean value
'''
def empty_struct( struct ):
    if struct: return False
    else: return True

''' README

Universal value for unavailable data

Return: 'N/A' in str type
'''
def invalid_val(): return 'N/A'

''' README

The basic cleaning that applies to the given text.

The following char will be cleared by this funct.:
  - '\n': new line
  - '\t': tab
  - '\r'
  - ',': comma

Return: text in str type
'''
def basic_cleaning( text ):
    return clean_str( clear_comma( text ) )

''' README

Clear several special chars in the given text.

The following char will be cleared by this funct.:
  - '\n': new line
  - '\t': tab
  - '\r'

Return: text in str type
'''
def clean_str( text ):
    return str(text).replace( '\n', '' ).replace( '\r', '' ).replace( '\t', '' )

''' README

Clear several chars in the given text (numeric).

The following char will be cleared by this funct.:
  - ',': comma
  - '.': dot

Return: text in str type
'''
def clean_num( text ):
    return clear_dot( clear_comma( text ) )

''' README

Clear all the sub-string in the given list within a given text.

Input:
  - text to be operated
  - list of sub-string to be removed

Return: text in str type
'''
def clear_multi_text( text, l=[] ):
    for e in l: text = text.replace( e, '' )
    return text

''' README

Clear all the chars in the given string of chars within a given text.

Input:
  - text to be operated
  - char string:
      for example, to remove ',', '.', and '|', input: ',.|'

Return: text in str type
'''
def clear_char( text, tar ):
    for t in tar: text = text.replace( t, '' )
    return text

''' README

Clear '.' (dot) in the given text.

Return: text in str type
'''
def clear_dot( text ):
    return str(text).replace( '.', '' )

''' README

Clear ',' (comma) in the given text.

Return: text in str type
'''
def clear_comma( text ):
    return str(text).replace( ',', '' )

''' README

Replace ',' (comma) with '-' (hyphen)

Return: text in str type
'''
def comma_to_hyphen( text ):
    return str(text).replace( ',', '-' )

''' README

Check if a given value is a numeric one

Input:
  - text to be transform
  - type: [ 'int', 'float' ]

Return: boolean value
'''
def is_numeric( val, type='float' ):
    val = str(val) # make sure it is not 'NoneType'
    try: # make sure the value is numeric
        if( type == 'int' ): val = int(val)
        else: val = float(val)
        return True
    except: return False

''' README

Make sure the value is numeric, otherwise return invalid_val().

Input:
  - text to be transform
  - type: [ 'int', 'float' ]

Return:
  - numeric value in str type
  - invalid_val()
'''
def numeric( val, type='float' ):
    if( is_numeric( val, type ) ): return str(val)
    else: return invalid_val()

''' README

Create numerical value. If failed, return invalid_val().

Input:
  - text to be transform
  - type: [ 'int', 'float' ]

Return:
  - numeric value in int/float type
  - invalid_val()
'''
def make_numeric( text, type='float' ):
    if( text != invalid_val() ):
        if( type == 'int' ): return int(text)
        else: return float(text)
    else: return invalid_val()

''' README

Delete duplicated entries within a given list.

Lib. dependency: pandas

Input: list of items

Return: list of items (deduplicated)
'''
def list_deduplicated( list_ ):
    df = pd.DataFrame.from_records( { 'item': list_ } )
    df = df.drop_duplicates()
    return df[ 'item' ].tolist()