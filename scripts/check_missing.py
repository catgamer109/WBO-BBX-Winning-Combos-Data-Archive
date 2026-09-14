import json

with open('extracted_data.json', 'r', encoding='utf-8') as f:
    extracted = json.load(f)
with open('wbo_parsed_events.json', 'r', encoding='utf-8') as f:
    parsed = json.load(f)
with open('compiled_challonge_stages.json', 'r', encoding='utf-8') as f:
    challonge = json.load(f)
with open('challonge_links.json', 'r', encoding='utf-8') as f:
    challonge_queue = json.load(f)
    
parsed_urls = {e['Event thread link'].lower() for e in parsed if 'Event thread link' in e}
challonge_urls = {e['URL'].lower().replace('http://', 'https://') for e in challonge if 'URL' in e}
challonge_queue_urls = {l.lower().replace('http://', 'https://') for l in challonge_queue}

missing_threads = set()
missing_brackets = set()

for e in extracted:
    l = e.get('event_page_link') or e.get('link')
    b = e.get('bracket_link')
    
    if l and 'worldbeyblade.org/thread-' in l.lower():
        if l.lower() not in parsed_urls:
            missing_threads.add(l)
            
    if b and 'challonge.com' in b.lower():
        b_clean = b.lower().replace('http://', 'https://')
        if b_clean not in challonge_urls and b_clean not in challonge_queue_urls:
            missing_brackets.add(b)

print("Missing Event Threads:", len(missing_threads))
print("Missing Brackets:", len(missing_brackets))

if missing_brackets:
    with open('new_missing_challonge.json', 'w', encoding='utf-8') as f:
        json.dump(list(missing_brackets), f, indent=2)
if missing_threads:
    with open('new_missing_threads.json', 'w', encoding='utf-8') as f:
        json.dump(list(missing_threads), f, indent=2)
