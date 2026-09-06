import json
import re

with open('extracted_data.json', 'r', encoding='utf-8') as f:
    extracted = json.load(f)

def clean_mangled_link(link):
    if not isinstance(link, str): return link
    if '...' in link: return link # keep truncated alone for now
    match = re.search(r'(https://worldbeyblade\.org/Thread-[A-Za-z0-9\-%]+--[0-9]{5,6}(?:(?:\?|&amp;)pid=[0-9]+(?:#pid[0-9]+)?)?)', link)
    if match:
        return match.group(1)
    return link

fixed_count = 0
for e in extracted:
    for key in ['link', 'event_page_link', 'event_name']:
        val = e.get(key)
        if val:
            new_val = clean_mangled_link(val)
            if new_val != val:
                e[key] = new_val
                fixed_count += 1

with open('extracted_data.json', 'w', encoding='utf-8') as f:
    json.dump(extracted, f, indent=2, ensure_ascii=False)

print(f"Fixed {fixed_count} mangled links.")

import subprocess
subprocess.run(['python', 'check_missing.py'])
