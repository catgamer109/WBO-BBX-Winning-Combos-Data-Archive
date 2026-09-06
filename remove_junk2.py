import json

junk = [
    "Will update once I get the combos from Kirito1696",
    "Forgot to take one"
]

data = json.load(open('extracted_data.json', encoding='utf-8'))
removed = 0
for e in data:
    for p in e.get('placements', []):
        combos = p.get('combos', [])
        new_combos = [c for c in combos if not any(j in c for j in junk) and not c.startswith("Vice Captain:") and not c.startswith("Blades:")]
        if len(new_combos) != len(combos):
            removed += (len(combos) - len(new_combos))
            p['combos'] = new_combos

if removed > 0:
    json.dump(data, open('extracted_data.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f"Removed {removed} junk sentences.")
else:
    print("None found.")
