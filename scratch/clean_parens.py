import json
import re

with open('compiled_data/extracted_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for event in data[-10:]:
    for placement in event.get('placements', []):
        new_combos = []
        for combo in placement.get('combos', []):
            cleaned = re.sub(r'\s*\([^)]*\)$', '', combo)
            new_combos.append(cleaned.strip())
        placement['combos'] = new_combos

with open('compiled_data/extracted_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
