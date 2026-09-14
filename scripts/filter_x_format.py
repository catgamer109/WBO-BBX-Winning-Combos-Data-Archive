import json
import pandas as pd

# Load the CSV
csv_file = 'event-threads/wbo_event_pages_multi_event.csv'
df = pd.read_csv(csv_file)

# Find links where 'full-page-html' does not contain 'X Format'
invalid_links = set()
for index, row in df.iterrows():
    html_content = str(row['full-page-html'])
    if 'X Format' not in html_content:
        invalid_links.add(row['web_scraper_start_url'])

print(f"Found {len(invalid_links)} links that do not contain 'X Format' in their HTML.")

# Load the extracted data
json_file = 'extracted_data.json'
with open(json_file, 'r', encoding='utf-8') as f:
    events = json.load(f)

# Filter events
initial_count = len(events)
filtered_events = [e for e in events if e.get('link') not in invalid_links]
final_count = len(filtered_events)

print(f"Filtered out {initial_count - final_count} events from JSON.")

# Save the updated extracted data
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(filtered_events, f, indent=2, ensure_ascii=False)

print("Updated extracted_data.json successfully.")
