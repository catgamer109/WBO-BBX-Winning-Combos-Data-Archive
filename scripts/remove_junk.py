import json

junk = [
    "(Aclarke25 tied 3rd place but I didn't have his winning combos)",
    "(a tiebreaker match was used to determine 4th)",
    "(late process as i was locked out of my email when my phone was messed)",
    "(Apr. 19, 2026 8:53 PM)BlockOfOk Wrote: Treasures of the Bey #3",
    "(My bad for posting the combos so late)",
    "(2/22/24) Dragoon but never forgotten"
]

data = json.load(open('extracted_data.json', encoding='utf-8'))
removed = 0
for e in data:
    for p in e.get('placements', []):
        combos = p.get('combos', [])
        new_combos = [c for c in combos if c not in junk]
        if len(new_combos) != len(combos):
            removed += (len(combos) - len(new_combos))
            p['combos'] = new_combos

if removed > 0:
    json.dump(data, open('extracted_data.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f"Removed {removed} junk sentences.")
else:
    print("None found.")
