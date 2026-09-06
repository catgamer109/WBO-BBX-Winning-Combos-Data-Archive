import json
import re

with open('wbo_parsed_events.json', 'r', encoding='utf-8') as f:
    events = json.load(f)

for e in events:
    cf = e.get("Custom format", "NOT FOUND")
    cf_lower = cf.lower()
    
    # 1. Catch unmapped seasonal ban lists
    if "summer season bans" in cf_lower or "banned parts" in cf_lower or "banned equipment" in cf_lower:
        e["Custom format"] = "Ban List"
        
    # 2. Catch stadium-restriction rule text masquerading as custom formats
    elif "played exclusively on" in cf_lower or "stadiums only" in cf_lower:
        e["Custom format"] = "NOT FOUND"
        
    # 3. Catch remaining section headers or boilerplate notices
    elif any(phrase in cf_lower for phrase in [
        "registration and general information", "directions and location information",
        "livestream and media information", "tournament information", "event information",
        "format information", "additional information", "need-to-know information",
        "contact information", "registration information", "banner by", "theweedybanditi"
    ]):
        e["Custom format"] = "NOT FOUND"
        
    # 4. Catch standard point-limit battle format descriptions
    elif "format: 3 on 3 battle" in cf_lower or "format: beyblade x | modified b4 g3" in cf_lower:
        e["Custom format"] = "NOT FOUND"

with open('wbo_parsed_events.json', 'w', encoding='utf-8') as f:
    json.dump(events, f, indent=2, ensure_ascii=False)

print("Cleanup complete! All lingering metadata and boilerplate text have been successfully scrubbed.")