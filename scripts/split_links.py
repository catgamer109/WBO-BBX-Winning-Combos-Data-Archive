import json
import pandas as pd
import numpy as np

# Load omit links
csv_file = 'event-threads/wbo_event_pages_multi_event_filtered.csv'
df = pd.read_csv(csv_file)
omit_links = set(df['web_scraper_start_url'].dropna().tolist())

# Load all links from JSON
json_file = 'extracted_data.json'
with open(json_file, 'r', encoding='utf-8') as f:
    events = json.load(f)

# Collect unique links, excluding the omit links
unique_links = set()
for e in events:
    link = e.get('link')
    # Filter out empty and omitted links
    if link and link not in omit_links:
        # The user was previously filtering only for "Thread" links
        if "Thread" in link and "Thread-Winning-Comb" not in link:
            unique_links.add(link)

unique_links = sorted(list(unique_links))
print(f"Total unique links remaining: {len(unique_links)}")

# Split into 3 chunks
chunks = np.array_split(unique_links, 3)

for i, chunk in enumerate(chunks):
    chunk_list = chunk.tolist()
    out_file = f"links_chunk_{i+1}.json"
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(chunk_list, f, indent=2, ensure_ascii=False)
    print(f"Saved {out_file} with {len(chunk_list)} links.")
