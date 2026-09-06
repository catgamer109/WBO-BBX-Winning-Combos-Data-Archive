import json

data = json.load(open('extracted_data.json', encoding='utf-8'))
removed = 0
for e in data:
    for p in e.get('placements', []):
        combos = p.get('combos', [])
        new_combos = []
        for c in combos:
            cl = c.lower().strip()
            # Remove anything ending with ':' like "Combos:" or "Name:"
            if cl.endswith(':'):
                continue
            # Remove isolated headers
            if cl in ['combos', 'winning combos', 'combo', 'winning combo']:
                continue
            if cl.startswith('combos '): # e.g. "COMBOS (BOTH STAGES):" is caught by ':' but just in case
                continue
            new_combos.append(c)
            
        if len(new_combos) != len(combos):
            removed += (len(combos) - len(new_combos))
            p['combos'] = new_combos

if removed > 0:
    json.dump(data, open('extracted_data.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f"Removed {removed} junk sentences.")
else:
    print("None found.")
