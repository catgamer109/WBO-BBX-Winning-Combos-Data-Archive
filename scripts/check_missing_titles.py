import pandas as pd
import json
from bs4 import BeautifulSoup

df = pd.read_csv('event-threads/wbo_event_pages_multi_event.csv')
threads = json.load(open('new_missing_threads.json', encoding='utf-8'))

open('titles.txt', 'w', encoding='utf-8').close()

for url in threads:
    match = df[df['web_scraper_start_url'] == url]
    with open('titles.txt', 'a', encoding='utf-8') as out:
        if len(match) > 0:
            html = match['full-page-html'].iloc[0]
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.title.string if soup.title else 'No Title'
            out.write(f"URL: {url}\nTitle: {title}\n\n")
        else:
            # Check by thread ID
            tid = url.split('--')[-1].split('?')[0].split('#')[0]
            match = df[df['web_scraper_start_url'].str.contains(tid)]
            if len(match) > 0:
                html = match['full-page-html'].iloc[0]
                soup = BeautifulSoup(html, 'html.parser')
                title = soup.title.string if soup.title else 'No Title'
                out.write(f"URL: {url}\nTitle: {title}\n\n")
            else:
                out.write(f"URL: {url}\nTitle: NOT FOUND IN CSV\n\n")

