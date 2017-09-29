from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import re
import pandas as pd
import numpy as np
from selenium import webdriver
from bs4 import BeautifulSoup
from natasha import Combinator
from natasha.grammars import Person, Organisation, Address, Street,Money, Date
import phonenumbers
pd.options.display.max_rows=200
pd.options.display.max_colwidth=200

def unique_list(l):

    """Takes unique words from parsed string"""

    ulist = []
    [ulist.append(x) for x in l if x not in ulist]

    return ulist


def read_data (name_of_file):

    """Read data from previous files"""

    links_df = pd.read_excel('../output/{}.xlsx'.format(name_of_file))
    links_df.columns=('link', 'url')
    links_df['uid'] = links_df['link'] + ' ' + links_df['url']
    links_df =  links_df.drop_duplicates(subset='uid', keep='first')
    links_df['url'] = links_df['url'].apply(lambda x : x.split('>')[0])
    links_df = links_df[:2]

    return links_df

def parse_text_from_links (links_df):

    """Parse data from links"""

    all_df = pd.DataFrame()
    all_text = []
    all_link = []
    all_uid = []
    all_url = []
    for url, link, uid in zip(links_df['url'], links_df['link'], links_df['uid']):
        print (url)
        browser.get(url)
        page = browser.page_source
        soup = BeautifulSoup(page)
        all_text.append(soup.text)
        all_url.append(url)
        all_link.append(link)
        all_uid.append(uid)
    temp_df = pd.concat([pd.DataFrame(all_url), pd.DataFrame(all_text), pd.DataFrame(all_link), pd.DataFrame(all_uid)],axis=1)
    temp_df.columns = ('url', 'text', 'link', 'uid')

    return temp_df

def parse_one_page (text, link, name_of_link):

    """Parse one text from one link"""

    text= text
    parsed_one = pd.DataFrame()

    combinator = Combinator([
        Person,
        Organisation,
        Address,
        Street,
        Money,
        Date
    ])

    matches = combinator.resolve_matches(
        combinator.extract(text), strict=False
    )
    matches = (
        (grammar, [t.value for t in tokens]) for (grammar, tokens) in matches
    )

    text_org = ''
    text_person = ''
    text_address = ''
    text_money = ''
    text_date = ''

    for i in matches:

        if str(i[0]).startswith('Organisation'):
            temp_value = ''
            for value in i[1]:
                temp_value+=str(value)
                temp_value+=' '
            text_org +=str(temp_value)

        elif str(i[0]).startswith('Person'):
            temp_value = ''
            for value in i[1]:
                temp_value+=str(value)
                temp_value+=' '
            text_person +=str(temp_value)

        elif str(i[0]).startswith('Address') | str(i[0]).startswith('Street') :
            temp_value = ''
            for value in i[1]:
                temp_value+=str(value)
                temp_value+=' '
            text_address +=temp_value

        elif str(i[0]).startswith('Money'):
            temp_value = ''
            for value in i[1]:
                temp_value+=str(value)
                temp_value+=' '
            text_money +=temp_value

        elif str(i[0]).startswith('Date'):
            temp_value = ''
            for value in i[1]:
                temp_value+=str(value)
                temp_value+=' '
            text_date +=temp_value

    text_phones = ''
    for match in phonenumbers.PhoneNumberMatcher(text, "RU"):
        text_phones+=str(phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164))
        text_phones+=' '

    text_org=' '.join(unique_list(text_org.split()))
    text_person=' '.join(unique_list(text_person.split()))
    text_address=' '.join(unique_list(text_address.split()))
    text_money=' '.join(unique_list(text_money.split()))
    text_phones=' '.join(unique_list(text_phones.split()))
    text_date=' '.join(unique_list(text_date.split()))
    parsed_one = pd.DataFrame()
    parsed_one = pd.DataFrame([name_of_link, link, text_org, text_person, text_address, text_money, text_phones, text_date]).T
    parsed_one.columns = ('name', 'link', 'organisation', 'person', 'address', 'money', 'phone', 'date')

    return parsed_one

def parse_all_pages (parsed):

    """Parse all texts"""

    final_df =pd.DataFrame()
    for text, link, name_of_link in zip(parsed['text'], parsed['url'], parsed['link']):

        try:
#         print (link)
            parsed_one = parse_one_page(text, link, name_of_link)
            final_df = pd.concat([final_df, parsed_one], axis=0)
        except:
            pass

    return final_df

def post_processing (final_df):

    """Merge with previous file and save"""

    estate = pd.read_excel('../output/parsed_estateline.xlsx')
    estate = pd.merge(estate, final_df, left_on='to_search', right_on='name', how='left')
    estate = estate[~estate['name'].isnull()]
    estate['count'] = estate.groupby('name')['to_search'].transform('count')
    estate = estate[estate['count']==2]
    del estate['count']
    estate.to_excel('../output/20170925_parsed_estateline_external_info.xlsx', index=False)

    return estate

### exceuting script
browser = webdriver.PhantomJS(executable_path='../../../usr/local/bin/phantomjs')
links_df = read_data('parsed_google')
parsed = parse_text_from_links(links_df)
final_df = parse_all_pages(parsed)
final_df.to_excel('../output/temp_to_del.xlsx', index=False)
# estateline_parsed = post_processing(final_df)
