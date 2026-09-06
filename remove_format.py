import json

def process_file():
    with open('wbo_parsed_events.json', 'r', encoding='utf-8') as f:
        events = json.load(f)
        
    for event in events:
        if 'Stadium type' in event:
            del event['Stadium type']
        if 'Custom format' in event:
            del event['Custom format']
            
    with open('wbo_parsed_events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
        
    print(f"Removed 'Stadium type' and 'Custom format' from {len(events)} events.")

if __name__ == '__main__':
    process_file()