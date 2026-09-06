import json

def clean():
    with open('extracted_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    cleaned_count = 0
    for event in data:
        for placement in event.get('placements', []):
            original = placement['player']
            if '"' in original or '\\' in original:
                cleaned = original.replace('"', '').replace('\\', '').strip()
                if cleaned != original:
                    placement['player'] = cleaned
                    cleaned_count += 1
                    
    with open('extracted_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"Cleaned quotes/backslashes from {cleaned_count} player names.")

if __name__ == '__main__':
    clean()
