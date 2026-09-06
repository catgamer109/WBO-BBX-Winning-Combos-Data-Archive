import json
import re

data = json.load(open('extracted_data.json', encoding='utf-8'))
fixed = 0

def clean_combo(c):
    original = c
    
    # 1. Strip all trailing parenthetical/bracketed statements
    while True:
        c_new = re.sub(r'\s*[\(\[][^\)\]]*[\)\]]\s*$', '', c)
        # Also catch unmatched opening parenthesis at the end (e.g. "Combo (First stage")
        c_new = re.sub(r'\s*\([^)]*$', '', c_new)
        if c_new == c:
            break
        c = c_new
        
    # 2. Strip known non-parenthetical stage tags at the end
    # Matches a dash or spaces followed by stage keywords, and optional filler words
    tag_pattern = r'\s*[-|]?\s*(?:both stages|first stage|final stage|group stage|top cut|finals|swiss)(?:\s+(?:only|and|&|or|final|stage|stages|both))*[^a-zA-Z0-9]*$'
    c = re.sub(tag_pattern, '', c, flags=re.IGNORECASE)
    
    return c.strip()

for e in data:
    for p in e.get('placements', []):
        combos = p.get('combos', [])
        new_combos = []
        for c in combos:
            cleaned = clean_combo(c)
            if cleaned != c:
                fixed += 1
            if cleaned: # Don't append empty strings
                new_combos.append(cleaned)
        p['combos'] = new_combos

if fixed > 0:
    json.dump(data, open('extracted_data.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f"Fixed {fixed} combos with trailing tags.")
else:
    print("None found.")
