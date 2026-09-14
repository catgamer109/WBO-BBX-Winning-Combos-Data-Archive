import json
import re

with open('wbo_parsed_events.json', 'r', encoding='utf-8') as f:
    parsed = json.load(f)

# Collect all valid URLs from parsed events
valid_urls = {e['Event thread link'] for e in parsed if 'Event thread link' in e}

# Also gather full urls from extracted data just in case
with open('extracted_data.json', 'r', encoding='utf-8') as f:
    extracted = json.load(f)
    
for e in extracted:
    l = e.get('event_page_link') or e.get('link')
    if l and '...' not in l and 'worldbeyblade.org' in l:
        valid_urls.add(l)

def resolve_truncated(truncated):
    if '...' not in truncated:
        return truncated
    parts = truncated.split('...')
    if len(parts) != 2:
        return truncated
    prefix, suffix = parts[0], parts[1]
    
    for url in valid_urls:
        if url.startswith(prefix) and url.endswith(suffix):
            return url
    return truncated

# Fix extracted_data.json
fixed_count = 0
for e in extracted:
    for key in ['link', 'event_page_link', 'event_name']:
        val = e.get(key)
        if val and isinstance(val, str) and '...' in val:
            resolved = resolve_truncated(val)
            if resolved != val:
                e[key] = resolved
                fixed_count += 1

with open('extracted_data.json', 'w', encoding='utf-8') as f:
    json.dump(extracted, f, indent=2, ensure_ascii=False)

print(f"Fixed {fixed_count} truncated links in extracted_data.json.")

# Run check_missing.py logic again to regenerate clean new_missing_threads.json
import subprocess
subprocess.run(['python', 'check_missing.py'])
