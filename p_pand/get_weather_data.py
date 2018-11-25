import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt

# All data from
# https://www.usclimatedata.com/climate/united-states/us


def get_state_dict():
    '''
    Prase HTML to collect state name and associated HREF
    ::return dictionary:: {'STATE_NAME':'HREF'}

    '''
    r = requests.get('https://www.usclimatedata.com/climate/united-states/us')
    html_source = r.text
    
    state_table_begin_search = 'Select a state by name'
    table_end = '</table>'

    states_dict = {}
    HREF_LIST = []

    # Find the index of the html source code that the HTML table of states and HREF's begins
    find_begin = html_source.index(state_table_begin_search)
    find_end = html_source[find_begin:].index(table_end) + find_begin

    # Slice HTML to just HTML table
    html_source = html_source[find_begin:find_end+1]

    # Get all HREF links
    cur_href = ''
    for i in range(len(html_source)):
        if html_source[i] == 'h':
            if html_source[i:i+6] == 'href="':
                # Once 'href="' is found, record HREF until link ends: href="/states/data/"
                for j in range(i+6, i+500):
                    if html_source[j] != '"':
                        cur_href += html_source[j]

                    else:
                        HREF_LIST.append(cur_href)
                        cur_href = ''
                        break

    # Use HREF links to create state:href dictionary
    # state is always in the URL
    for href in HREF_LIST:
        sub_set = href.split('/')
        # the index of 2 is always the state
        states_dict[sub_set[2]] = href
        
    return states_dict


def get_data_from_state_page(state_href):
    '''
    ::param state_href:: string --> href to a state data page
    ::return list of dictionaries:: {'Month': string, 'Low': float, 'High': float, 'Precipitation': float}
    '''
    base_url = 'https://www.usclimatedata.com'
    url = base_url + state_href
    
    # Each state page has a list of dictionaries with all desired data
    # stored in a javascript variable called 'the_data'
    start_key = "var the_data = '["
    end_key = "]';"

    r = requests.get(url)
    html_source = r.text

    # Find the 'the_data' variable contents and slice HTML to just that
    start = html_source.index(start_key)
    html_source = html_source[start + len(start_key):]
    end = html_source.index(end_key)
    html_source = html_source[:end]

    # Split the string into individual dictionaries
    # '[{}, {}, {}]' --> [{, '', '', '', }]
    source_dicts = html_source.split('},{')

    # Restore proper python dictionary syntax
    for index, elm in enumerate(source_dicts):
        if index == 0:
            source_dicts[index] = elm + '}'

        elif index == len(source_dicts) - 1:
            source_dicts[index] = '{' + elm

        else:
            source_dicts[index] = '{' + elm + '}'

    # Eval all string elements of list to python dictionaries
    for index, item in enumerate(source_dicts):
        source_dicts[index] = eval(item)

    return source_dicts


def create_data_frame_dict(progress=False):
    '''
    ::return dictionary:: tuple keys, dictionary values

    Create the expected input for pandas '.from_dict' method
    with tuples as keys (multiIndex) and dictionary as values (columns)

    If the values are lists, the tuple index will be interpreted as a single index level
    If the values are dictionaries, the tuple index will be unpacked for multi level Index
    ^I'm not really sure why, but thank you stack overflow:
    #https://stackoverflow.com/questions/53219207/dataframe-from-dict-fails-to-change-dict-with-tuple-keys-into-multi-index-datafr
    '''
    data_frame_dict = {}
    states_dict = get_state_dict()

    # Format each state's data as:
    # {(state, month): {Low, High, Precipitation}}
    count = 0
    for state, href in states_dict.items():
        if progress:
            count += 1
            print('Getting state: {}'.format(count))
        source_dict = get_data_from_state_page(href)
        for sub_dict in source_dict:
            data_frame_dict[ (state, sub_dict['Month']) ] = {'Low': sub_dict['Low'],
                                                             'High': sub_dict['High'],
                                                             'Precipitation': sub_dict['Precipitation']
                                                             }

    return data_frame_dict


def get_df(**kwargs):
    '''
    ::param progress:: Default False, log state data collection progress
    
    ::return pandas Dataframe::

                  Low    High   Precipitation
    State   Month  
    Alabama  Jan  int64  int64  float64
    '''
    dframe_dict = create_data_frame_dict(**kwargs)
    df = pd.DataFrame.from_dict(dframe_dict, orient='index', columns=['Low', 'High', 'Precipitation'])
    df.index.names = ['State', 'Month']

    return df

if __name__ == '__main__':
    df = get_df()
    print(df.head())
    print(df.dtypes)
    print(df.describe())


