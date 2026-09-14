import json

# Remove from extracted_data.json
with open('extracted_data.json', 'r', encoding='utf-8') as f:
    extracted = json.load(f)

extracted = [e for e in extracted if '109563' not in (e.get('link') or '')]

with open('extracted_data.json', 'w', encoding='utf-8') as f:
    json.dump(extracted, f, indent=2, ensure_ascii=False)

# Remove from wbo_parsed_events.json
with open('wbo_parsed_events.json', 'r', encoding='utf-8') as f:
    parsed = json.load(f)

parsed = [e for e in parsed if '109563' not in (e.get('Event thread link') or '')]

with open('wbo_parsed_events.json', 'w', encoding='utf-8') as f:
    json.dump(parsed, f, indent=2, ensure_ascii=False)

print("Removed thread 109563 from both datasets.")
