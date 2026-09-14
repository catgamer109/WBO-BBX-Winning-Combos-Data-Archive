import pandas as pd
from bs4 import BeautifulSoup
import json
import re

def parse_post(row):
    html_content = row['post-content']
    author = row['author']
    post_date = row['post-date']
    
    if pd.isna(html_content):
        return []
        
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove signatures
    for sig in soup.find_all('div', class_='post-signature'):
        sig.decompose()
        
    events = []
    
    # Let's just print the text to see how to split it
    text = soup.get_text(separator='\n').strip()
    return {'author': author, 'date': post_date, 'text': text}

df = pd.read_csv('wbo_bbx_combos_with_dates.csv')
print(json.dumps([parse_post(row) for _, row in df.dropna(subset=['post-content']).head(3).iterrows()], indent=2))
