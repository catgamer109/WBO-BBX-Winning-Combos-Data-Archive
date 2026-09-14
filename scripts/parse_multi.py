import pandas as pd
import json
import re

df = pd.read_csv('wbo_bbx_combos_with_dates.csv')

multi_event_posts = []

for _, row in df.dropna(subset=['post-content']).iterrows():
    html_content = row['post-content']
    
    # Simple heuristic: if "1st" appears more than once, it might be multiple events
    # We should look for "1st" or "1st Place" outside of quotes or just as text.
    if html_content.lower().count('1st') > 1:
        multi_event_posts.append(row['post-content'])
        if len(multi_event_posts) >= 3:
            break
            
print(json.dumps(multi_event_posts, indent=2))
