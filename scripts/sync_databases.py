import json

with open('compiled_data/extracted_data.json', 'r', encoding='utf-8') as f:
    extracted = json.load(f)

with open('compiled_data/wbo_parsed_events.json', 'r', encoding='utf-8') as f:
    parsed = json.load(f)

parsed_urls = {e['Event thread link'].lower() for e in parsed if 'Event thread link' in e}

filtered = []
for e in extracted:
    l = e.get('event_page_link') or e.get('link')
    if l and l.lower() in parsed_urls:
        filtered.append(e)

with open('compiled_data/extracted_data.json', 'w', encoding='utf-8') as f:
    json.dump(filtered, f, indent=2, ensure_ascii=False)

print(f"Kept {len(filtered)} events. Dropped {len(extracted) - len(filtered)} events.")

import subprocess
subprocess.run(['python', 'check_missing.py'])
