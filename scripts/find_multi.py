import json
import pandas as pd
from bs4 import BeautifulSoup
from collections import defaultdict

# load json
with open('extracted_data.json', 'r', encoding='utf-8') as f:
    events = json.load(f)

# group by author and post_date
post_map = defaultdict(list)
for ev in events:
    author = ev.get('author')
    post_date = ev.get('post_date')
    post_link = ev.get('link')
    if author and post_date:
        post_map[(author, post_date)].append(post_link)

# load csv to get all links
df = pd.read_csv('wbo_bbx_combos_with_dates.csv')
# Clean non-breaking spaces in CSV dates to match JSON dates
df['post-date-clean'] = df['post-date'].astype(str).str.replace('\xa0', ' ')

with open('multi_event_posts.md', 'w', encoding='utf-8') as out:
    out.write("# Multi-Event Posts\n\n")
    
    count = 0
    for (author, post_date), ev_links in post_map.items():
        # filter out None and get unique links
        unique_links = set(l for l in ev_links if l)
        
        # User requested: "don't include them as a multi post if they have the same link"
        if len(unique_links) > 1:
            count += 1
            # find the post in df
            matching = df[(df['author'] == author) & (df['post-date-clean'] == post_date)]
            
            out.write(f"### Post by {author} on {post_date}\n")
            out.write(f"- **Number of distinct event links extracted:** {len(unique_links)}\n")
            out.write(f"- **Distinct Event Links:** {', '.join(unique_links)}\n")
            
            if not matching.empty:
                content = matching.iloc[0]['post-content']
                soup = BeautifulSoup(content, 'html.parser')
                links = []
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if 'Thread' in href:
                        links.append(href)
                
                if links:
                    out.write(f"- **Links inside CSV HTML:** {', '.join(links)}\n")
                else:
                    out.write("- **Links inside CSV HTML:** None\n")
            else:
                out.write("- **Links inside CSV HTML:** *Post not found in CSV.*\n")
                
            out.write("\n---\n\n")
            
    out.write(f"Total multi-event posts found: {count}\n")

print(f"Finished. Found {count} multi-event posts.")
