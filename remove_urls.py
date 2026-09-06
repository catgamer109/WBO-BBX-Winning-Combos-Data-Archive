import json
import re

data = json.load(open('extracted_data.json', encoding='utf-8'))
removed = 0
for e in data:
    for p in e.get('placements', []):
        combos = p.get('combos', [])
        new_combos = []
        for c in combos:
            if 'http://' in c or 'https://' in c or 'Footage of' in c:
                continue
            new_combos.append(c)
            
        if len(new_combos) != len(combos):
            removed += (len(combos) - len(new_combos))
            p['combos'] = new_combos

if removed > 0:
    json.dump(data, open('extracted_data.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f"Removed {removed} URL/Footage sentences.")
else:
    print("None found.")
