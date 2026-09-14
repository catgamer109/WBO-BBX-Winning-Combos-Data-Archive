import json
import re

def get_thread_id(url):
    if not url:
        return None
    match = re.search(r'--(\d+)', url)
    if match:
        return match.group(1)
    match = re.search(r'Thread-.*?(\d+)', url)
    if match:
        return match.group(1)
    return None

def format_stage(settings):
    if not settings:
        return None
    # Settings has keys: "Bracket type", "Battle Type", "Match Type"
    parts = []
    bt = settings.get("Battle Type")
    if bt and bt != "NOT FOUND":
        parts.append(bt)
    brkt = settings.get("Bracket type")
    if brkt and brkt != "NOT FOUND":
        parts.append(brkt)
    mt = settings.get("Match Type")
    if mt and mt != "NOT FOUND":
        parts.append(mt)
        
    if not parts:
        return None
    return " ".join(parts).title().replace("3On3", "3on3").replace("1On1", "1on1")

def main():
    import sys
    events_file = sys.argv[1] if len(sys.argv) > 1 else 'compiled_data/wbo_parsed_events.json'
    print(f"Loading {events_file}...")
    with open(events_file, 'r', encoding='utf-8') as f:
        parsed_events = json.load(f)
        
    print("Building metadata dictionary...")
    metadata_map = {}
    for ev in parsed_events:
        url = ev.get("Event thread link")
        if url:
            metadata_map[url] = ev
            if '#' in url:
                metadata_map[url.split('#')[0]] = ev
            if url.startswith('https:'):
                metadata_map[url.replace('https:', 'http:')] = ev
                if '#' in url:
                    metadata_map[url.split('#')[0].replace('https:', 'http:')] = ev
            
    print("Loading extracted_data.json...")
    with open('compiled_data/extracted_data.json', 'r', encoding='utf-8') as f:
        extracted_data = json.load(f)
        
    print("Merging metadata...")
    matched_count = 0
    unmatched = []
    
    for e in extracted_data:
        # Delete optional_rules entirely
        if "optional_rules" in e:
            del e["optional_rules"]
            
        link = e.get("link") or e.get("event_name")
        if not link:
            continue
            
        meta = metadata_map.get(link)
        if not meta and '#' in link:
            meta = metadata_map.get(link.split('#')[0])
            
        if meta:
            
            # Map fields
            e["explicit_event_name"] = meta.get("Tournament name")
            e["event_date"] = meta.get("Event date")
            e["event_page_link"] = meta.get("Event thread link")
            
            bracket_link = meta.get("Bracket link")
            if bracket_link and bracket_link != "NOT FOUND":
                # If it's a list with 1 element, just store the string. If > 1, store list.
                if len(bracket_link) == 1:
                    e["bracket_link"] = bracket_link[0]
                else:
                    e["bracket_link"] = bracket_link
            
            e["ranked_status"] = meta.get("Ranked or unranked")
            
            player_count = meta.get("Player count", {}).get("Actual attendees")
            if player_count and player_count != "NOT FOUND":
                e["player_count"] = player_count
                
            loc = meta.get("Location")
            if loc and loc != "NOT FOUND":
                e["location"] = loc
                
            fs = format_stage(meta.get("First Stage Settings"))
            if fs: e["first_stage_format"] = fs
            
            fss = format_stage(meta.get("Final Stage Settings"))
            if fss: e["final_stage_format"] = fss
            
            matched_count += 1
        else:
            if link:
                unmatched.append(link)

    print(f"Matched and merged metadata for {matched_count} events.")
    print(f"Could not find metadata for {len(unmatched)} events.")
    
    # Save the updated data
    print("Saving updated extracted_data.json...")
    with open('compiled_data/extracted_data.json', 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, indent=2, ensure_ascii=False)
    print("Done!")

if __name__ == '__main__':
    main()
