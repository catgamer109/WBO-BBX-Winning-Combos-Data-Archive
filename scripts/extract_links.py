import json

with open('compiled_data/extracted_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Only process the newly added events from the latest CSV
data = data[-10:]

thread_links = []
challonge_links = []

for event in data:
    if event.get('link'):
        thread_links.append(event['link'])
    elif event.get('event_page_link'):
        thread_links.append(event['event_page_link'])

    if event.get('bracket_link'):
        challonge_links.append(event['bracket_link'])

# Deduplicate links while preserving order
thread_links = list(dict.fromkeys(thread_links))
challonge_links = list(dict.fromkeys(challonge_links))

with open('new_extracted_thread_links.json', 'w', encoding='utf-8') as f:
    json.dump(thread_links, f, indent=2, ensure_ascii=False)

with open('new_extracted_challonge_links.json', 'w', encoding='utf-8') as f:
    json.dump(challonge_links, f, indent=2, ensure_ascii=False)

print(f"Extracted {len(thread_links)} thread links and {len(challonge_links)} challonge links.")
