import re
import pandas as pd
import numpy as np
from selenium import webdriver
from bs4 import BeautifulSoup
import time
from collections import  Counter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import datetime
from time import strftime, gmtime
# import ipyslack
# %load_ext ipyslack
# %slack_setup -t xoxp-193472796262-192716443172-193493151111-04ee68d0610db8a5d78ea6c451414f8a -c #general

date_time = datetime.datetime.now()


# service_args=['--proxy=us-wa.proxymesh.com:31280'

browser = webdriver.PhantomJS(executable_path='/../usr/local/bin/phantomjs')

def split_on_simbol (df, col, smb, name):

    """Splits columns into two parts"""

    new_df = pd.DataFrame(df[col].str.split(smb, 0).tolist())
    df = pd.concat([df.reset_index(drop=True), new_df],axis=1)
    del df[col]
    df = df.rename(columns={0:name+'_0', 1:name+'_1'})
    return df

def estateline_format (parsed_df):

    """Converts data to proper format"""

    parsed_df = parsed_df[parsed_df['id'] != 'ID']
    parsed_df['id'] = parsed_df['id'].apply(lambda text : int(re.sub('\n', '', text)))
    parsed_df = split_on_simbol(parsed_df, 'info', u'\nпремиум\nпросмотрено\n', 'info')
    parsed_df = split_on_simbol(parsed_df, 'class', u' » ', 'class')
    parsed_df =split_on_simbol(parsed_df, 'geo', u' » ', 'geo')
    parsed_df =split_on_simbol(parsed_df, 'geo_0', u'Район: ', 'geo_split')

    for col in parsed_df.columns:
        try:
            parsed_df[col] = parsed_df[col].apply(lambda text : re.sub('\n', '', text))
        except:
            pass
    parsed_df = parsed_df.rename(columns = {'geo_1': 'district', 'geo_split_0': 'city', 'geo_split_1': 'area'})
    return parsed_df


def estateline_parse_page (num_page):

    """Parses one page from Estateline web-site"""

    browser.get('http://estateline.ru/projects/all/msk/?stPage={}'.format(num_page))
    time.sleep(2)
    page = browser.page_source
    soup = BeautifulSoup(page)
    long_text = []
    for value in soup.find_all('td', class_=["first", "name", "geo", "type"]):
        long_text.append(value.text)
        temp_df = pd.DataFrame(long_text)
    temp_df = temp_df.reindex(temp_df.index.drop(0))
    count = int(temp_df.shape[0]/4)
    temp_df = temp_df.reset_index(drop=True)
    temp_df['ind'] = sorted(list(range(count))*4)
    all_df = pd.DataFrame()
    for i in temp_df['ind'].unique():
        one_df = temp_df[temp_df['ind']==i].T
        one_df.columns = ('id', 'info', 'class', 'geo')
        one_df = one_df.reindex(one_df.index.drop('ind'))
        all_df = pd.concat([all_df, one_df])
    return all_df

def estateline_parse_all (number_of_pages):

    """Parses data from multiple pages"""

    today_time = strftime("%Y-%m-%d_%H-%M-%S", gmtime())
    all_pages = pd.DataFrame()
    for i in range(number_of_pages):
        print (i+1)
        one_page = estateline_parse_page(i+1)
        one_page['parsing_time'] = today_time
        one_page['page_number'] = i+1
        all_pages = pd.concat([all_pages, one_page])
    return all_pages


parsed_df = estateline_parse_all(2)
print ('parsed 1 page')
formated_df = estateline_format(parsed_df)
formated_df.to_excel('temp.xlsx', index=False)
