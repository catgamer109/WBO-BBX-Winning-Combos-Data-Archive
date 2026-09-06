import json
import re

with open('extracted_data.json', 'r', encoding='utf-8') as f:
    extracted = json.load(f)

def clean_challonge(link):
    if not isinstance(link, str): return link
    if 'challonge.com/' not in link: return link
    
    # Keep up to the first path segment after challonge.com/
    # This strips trailing slashes, /standings, /groups, ?queryparams, etc.
    match = re.search(r'(https?://(?:[a-zA-Z0-9-]+\.)?challonge\.com/[^/\?\#]+)', link)
    if match:
        return match.group(1)
    return link

fixed_count = 0
for e in extracted:
    val = e.get('bracket_link')
    if val:
        new_val = clean_challonge(val)
        if new_val != val:
            e['bracket_link'] = new_val
            fixed_count += 1

with open('extracted_data.json', 'w', encoding='utf-8') as f:
    json.dump(extracted, f, indent=2, ensure_ascii=False)

print(f"Fixed {fixed_count} Challonge links.")

import subprocess
subprocess.run(['python', 'check_missing.py'])
