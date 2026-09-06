import pandas as pd
import glob
import os
import re

csvs = glob.glob('event-threads/beyblade X events/*.csv')
found = False

for f in csvs:
    df = pd.read_csv(f)
    for _, r in df.iterrows():
        if '128149' in str(r.get('web_scraper_start_url', '')):
            html = str(r.get('full-page-html', ''))
            links = set(re.findall(r'https?://[^\s\"\']*challonge\.com[^\s\"\']*', html))
            print(f"Found in {f}")
            print(f"Links: {links}")
            found = True

if not found:
    print('Not found')
