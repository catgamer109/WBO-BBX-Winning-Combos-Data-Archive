import pandas as pd
from bs4 import BeautifulSoup
import re

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

df = pd.read_csv('wbo_bbx_combos/wbo_bbx_combos_with_dates.csv')
texts = df[df['post-content'].str.contains('pid1880298', na=False)]['post-content']
if len(texts) > 0:
    text = texts.iloc[0]
    soup = BeautifulSoup(text, 'html.parser')
    links = {clean_text(a.get_text()): a.get('href') for a in soup.find_all('a')}
    print(links)
