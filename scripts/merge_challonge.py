import json
import re

wbo_events = json.load(open('wbo_parsed_events.json', encoding='utf-8'))
challonge_data = json.load(open('compiled_challonge_stages.json', encoding='utf-8'))

c_dict = {}
for c in challonge_data:
    c_dict[c['URL'].lower()] = c

updated_count = 0

for ev in wbo_events:
    links = ev.get('Bracket link', [])
    if isinstance(links, str):
        if links == 'NOT FOUND':
            links = []
        else:
            links = [links]
            
    clean_links = []
    for l in links:
        match = re.match(r'^(https?://[^/]+)(.*)$', l, re.IGNORECASE)
        if match: 
            l = match.group(1).lower() + match.group(2)
        if '#' in l: 
            l = l.split('#')[0]
        l = l.rstrip('/')
        for suffix in ['/standings', '/participants', '/stations', '/settings', '/issues', '/groups']:
            if l.endswith(suffix): 
                l = l[:-len(suffix)]
                break
        clean_links.append(l)
        
    found_c = [c_dict[l.lower()] for l in clean_links if l.lower() in c_dict]
    
    first_fmt, final_fmt = None, None
    first_pts, final_pts = None, None
    player_count = None
    
    if len(found_c) == 1:
        c = found_c[0]
        player_count = c.get('Player Count')
        
        if len(clean_links) > 1 and ('final' in c['URL'].lower() or 'top' in c['URL'].lower() or 'cut' in c['URL'].lower()):
            final_fmt = c['First Stage Format'] or c['Final Stage Format']
            final_pts = c['First Stage Points'] or c['Final Stage Points']
        else:
            first_fmt = c['First Stage Format']
            final_fmt = c['Final Stage Format']
            first_pts = c['First Stage Points']
            final_pts = c['Final Stage Points']
            
    elif len(found_c) > 1:
        # Safely extract the highest player count among multiple linked brackets
        p_counts = [c.get('Player Count') for c in found_c if c.get('Player Count') is not None]
        if p_counts:
            player_count = max(p_counts)
            
        for c in found_c:
            if c['First Stage Format'] and c['Final Stage Format']:
                first_fmt = c['First Stage Format']
                final_fmt = c['Final Stage Format']
                first_pts = c['First Stage Points']
                final_pts = c['Final Stage Points']
                break
                
        if not first_fmt:
            final_c = None
            first_c = None
            for c in found_c:
                fmt = c['First Stage Format'] or c['Final Stage Format']
                if fmt in ['single elimination', 'double elimination']:
                    final_c = c
                else:
                    first_c = c
            
            if first_c:
                first_fmt = first_c['First Stage Format'] or first_c['Final Stage Format']
                first_pts = first_c['First Stage Points'] or first_c['Final Stage Points']
            if final_c:
                final_fmt = final_c['First Stage Format'] or final_c['Final Stage Format']
                final_pts = final_c['First Stage Points'] or final_c['Final Stage Points']

    changed = False
    if first_fmt or first_pts or final_fmt or final_pts or (player_count is not None):
        changed = True

    if first_fmt:
        if not isinstance(ev.get('First Stage Settings'), dict):
            ev['First Stage Settings'] = {"Bracket type": "NOT FOUND", "Battle Type": "NOT FOUND", "Match Type": "NOT FOUND"}
        ev['First Stage Settings']['Bracket type'] = first_fmt
    if first_pts:
        if not isinstance(ev.get('First Stage Settings'), dict):
            ev['First Stage Settings'] = {"Bracket type": "NOT FOUND", "Battle Type": "NOT FOUND", "Match Type": "NOT FOUND"}
        ev['First Stage Settings']['Match Type'] = first_pts
        
    if final_fmt:
        if not isinstance(ev.get('Final Stage Settings'), dict):
            ev['Final Stage Settings'] = {"Bracket type": "NOT FOUND", "Battle Type": "NOT FOUND", "Match Type": "NOT FOUND"}
        ev['Final Stage Settings']['Bracket type'] = final_fmt
    if final_pts:
        if not isinstance(ev.get('Final Stage Settings'), dict):
            ev['Final Stage Settings'] = {"Bracket type": "NOT FOUND", "Battle Type": "NOT FOUND", "Match Type": "NOT FOUND"}
        ev['Final Stage Settings']['Match Type'] = final_pts

    if player_count is not None:
        if not isinstance(ev.get('Player count'), dict):
            ev['Player count'] = {"Actual attendees": "NOT FOUND", "Cap": "NOT FOUND"}
        ev['Player count']['Actual attendees'] = str(player_count)

    if changed:
        updated_count += 1

with open('wbo_parsed_events.json', 'w', encoding='utf-8') as f:
    json.dump(wbo_events, f, indent=2)

print(f"Updated {updated_count} events in wbo_parsed_events.json")