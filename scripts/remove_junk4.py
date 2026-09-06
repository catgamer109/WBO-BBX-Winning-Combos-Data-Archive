import json

junk = [
    "?? (Still waiting on his combinations)",
    "I dont think that was me, Jedi? I dont use Buster and that deck has 2 1-60 in it?",
    "https://www.youtube.com/watch?v=z4lwQ7kAg1M"
]

data = json.load(open('extracted_data.json', encoding='utf-8'))
removed = 0
for e in data:
    for p in e.get('placements', []):
        combos = p.get('combos', [])
        new_combos = []
        for c in combos:
            if c in junk:
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
