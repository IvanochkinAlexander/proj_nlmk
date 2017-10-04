from GoogleScraper import scrape_with_config, GoogleSearchError
import random
import pandas as pd
import numpy as np
import time

formated_df = pd.read_excel('../output/parsed_estateline.xlsx')

keywords = formated_df['to_search'][:5].values

# See in the config.cfg file for possible values
keywords_all = []
links_all = []
for keyword in keywords:

    config = {
            'use_own_ip': True,
            'keyword': keyword+ ' -site:poiskstroek.ru -site:rusdevelopers.ru -site:estateline -site:stroiman.ru -site:cian.ru -site:domofond.ru',
            'search_engines': ['duckduckgo'],
            'num_pages_for_keyword': 1,
            'num_results_per_page': 4,
            'scrape_method': 'selenium',
            'sel_browser': 'phantomjs',
    }

    try:
        search = scrape_with_config(config)
    except GoogleSearchError as e:
        print(e)

    # let's inspect what we got. Get the last search:
    keyword_one = []
    links_one = []
    for serp in search.serps:
    #     print(serp)
        for link in serp.links[:2]:
            links_one.append(link)
            keyword_one.append(keyword)
    keywords_all.append(keyword_one)
    links_all.append(links_one)
    time.sleep(random.choice(range(20,30)))

links_all_flat = [item for sublist in links_all for item in sublist]
keywords_all_flat = [item for sublist in keywords_all for item in sublist]
parsed_df_all = pd.DataFrame(links_all_flat, keywords_all_flat).reset_index()
parsed_df_all[0] = parsed_df_all[0].apply(lambda x : str(x).split('has url:')[1].split('/>')[0])
parsed_df_all

parsed_df_all.to_excel('../output/parsed_google.xlsx', index=False)
