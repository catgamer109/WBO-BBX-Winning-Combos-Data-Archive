import json
import re

data = json.load(open('extracted_data.json', encoding='utf-8'))
fixed = 0
for e in data:
    for p in e.get('placements', []):
        combos = p.get('combos', [])
        new_combos = []
        for c in combos:
            # Strip leading dashes, spaces, asterisks, and bullet points
            cleaned = re.sub(r'^[\-\s*•]+', '', c)
            if cleaned != c:
                fixed += 1
            new_combos.append(cleaned)
        p['combos'] = new_combos

if fixed > 0:
    json.dump(data, open('extracted_data.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f"Fixed {fixed} combos with leading dashes/bullets.")
else:
    print("None found.")
