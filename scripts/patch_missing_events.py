import json
import csv
import re
from bs4 import BeautifulSoup

links_to_patch = [
    "https://worldbeyblade.org/Thread-Preparing-for-the-Grand-Prix--108856",
    "https://worldbeyblade.org/Thread-Sharknado-3-Oh-Hell-s-Scythe-No--109675",
    "https://worldbeyblade.org/Thread-Beyblade-X-Showdown-at-X-City--109874",
    "https://worldbeyblade.org/Thread-TableTop-Tavern-s-Beyblade-X-Tournament-for-June-8th-UX-04-Battle-Entry-Set-for-1st--111602",
    "https://worldbeyblade.org/Thread-TableTop-Tavern-s-Beyblade-X-Tournament-for-August-3rd--112430?pid=1868730#pid1868730",
    "https://worldbeyblade.org/Thread-Multi-Madness-Dran-Draft--112834",
    "https://worldbeyblade.org/Thread-Kamen-X-Bird-Multi-California-s-first-STOCK-X-Tournament-Invite-Only--113497",
    "https://worldbeyblade.org/Thread-Edmonton-AB-Spooktacular-Showdown-2024--113543",
    "https://worldbeyblade.org/Thread-The-Nerd-Mall-New-Year-Bash--114845",
    "https://worldbeyblade.org/Thread-National-Championship-Qualifier-Bristol--115370",
    "https://worldbeyblade.org/Thread-Bey-X-Andria-4-Immure--115294",
    "https://worldbeyblade.org/Thread-Curio-Clash--115881",
    "https://worldbeyblade.org/Thread-Krakenhits-X-Beyblade-Tournament-9--116889",
    "https://worldbeyblade.org/Thread-Bongo-Bash-4-CardArt--118037",
    "https://worldbeyblade.org/Thread-Clash-of-Blades-6--118920",
    "https://worldbeyblade.org/Thread-Top-Deck-Games-Cherry-Hill-Beyblade-X-Tournament-1--118859",
    "https://worldbeyblade.org/Thread-Clash-of-Blades-8--119519",
    "https://worldbeyblade.org/Thread-Beys-in-the-Basement--120579",
    "https://worldbeyblade.org/Thread-West-Coast-Beyblade-TT-Series-ft-Sabrina-Carpenter--119565",
    "https://worldbeyblade.org/Thread-Top-Cut-Battle-League-10-20--121011",
    "https://worldbeyblade.org/Thread-ELXGSL-AWARD-CEREMONY-DBA-X-March-Madness-Ranked",
    "https://worldbeyblade.org/Thread-Dallas-Beyblade-Association-March-Madness-Ranked-2",
    "https://worldbeyblade.org/Thread-Decks-and-Dice-BBX-Weekly-Tournament-16--124254",
    "https://worldbeyblade.org/Thread-Dallas-Beyblade-Association-March-Madness-3--124370",
    "https://worldbeyblade.org/Thread-Dallas-Beyblade-Association-March-Madness-4--124371",
    "https://worldbeyblade.org/Thread-Dallas-Beyblade-Association-Randy-s-Rhino-Ranch-Limited-4--124721",
    "https://worldbeyblade.org/Thread-Dallas-Beyblade-Association-H%C3%A9ctors-Tyranno-Park-Classic-7--124857",
    "https://worldbeyblade.org/Thread-Dallas-Beyblade-Association-JRF-S-Pegasi-Race-CX-3--125005",
    "https://worldbeyblade.org/Thread-Dallas-Beyblade-Association-Angelo-s-Dragoon-Blitz-Open-14--125199",
    "https://worldbeyblade.org/Thread-Dallas-Beyblade-Association-Lui-s-Homage-Showdown-Classic-8--125418",
    "https://worldbeyblade.org/Thread-Dallas-Beyblade-Association-Katira-s-Feline-Frenzy-Limited-5--125518",
    "https://worldbeyblade.org/Thread-Dallas-Beyblade-Association-Lucius-Dark-Revival-Limited-6--125565",
    "https://worldbeyblade.org/Thread-Dallas-Beyblade-Association-Hasbro-s-Animal-Planet-CX-4--125714",
    "https://worldbeyblade.org/Thread-Dallas-Beyblade-Association-Open-15--125821",
    "https://worldbeyblade.org/Thread-Dallas-Beyblade-Association-Blayde-s-Doro-Catastrophe-Open-16",
    "https://worldbeyblade.org/Thread-Dallas-Beyblade-Association-Duel-Of-The-Fates-2-Classic-9--126074",
    "https://worldbeyblade.org/Thread-Dallas-Beyblade-Association-Classic-10--126165",
    "https://worldbeyblade.org/Thread-Dallas-Beyblade-Association-Limited-7--126228",
    "https://worldbeyblade.org/Thread-Dallas-Beyblade-Association-Beycon-Regional-Scrims-Standard-17--126263",
    "https://worldbeyblade.org/Thread-Dallas-Beyblade-Association-Beycon-26-Dallas-Regionals",
    "https://worldbeyblade.org/Thread-Dallas-Beyblade-Association-Breaking-Limits-Limited-8--127078",
    "https://worldbeyblade.org/Thread-Dallas-Beyblade-Association-The-Beycon-Blitz-Standard-18--127339",
    "https://worldbeyblade.org/Thread-DMVBXL-Team-Battle-Manassas-08-15-26--127006",
    "https://worldbeyblade.org/Thread-Dallas-Beyblade-Association-Limited-9--128074",
    "https://worldbeyblade.org/Thread-Dallas-Beyblade-Association-The-Mid-Season-Cup-at-The-Denton-Card-Show",
    "https://worldbeyblade.org/Thread-Dallas-Beyblade-Association-Classic-12--128076"
]

def is_combo(line):
    line = line.strip()
    if not line: return False
    if len(line) > 50: return False
    
    # Must contain a number (for ratchet/bit)
    if not re.search(r'\d', line): return False
    
    # Exclude obvious non-combos
    lower = line.lower()
    if 'stadium' in lower or 'format' in lower or 'rule' in lower or 'deck list' in lower or 'side deck' in lower:
        return False
    if 'place' in lower and ('1st' in lower or '2nd' in lower or '3rd' in lower):
        return False
        
    return True

def extract_combos_from_html(html_text):
    if not html_text: return []
    soup = BeautifulSoup(html_text, 'html.parser')
    text = soup.get_text(separator='\n')
    
    lines = text.split('\n')
    placements = []
    
    current_rank = None
    current_player = None
    current_combos = []
    
    in_side_deck = False
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # Check for side deck
        if 'side deck' in line.lower() or 'side board' in line.lower() or 'sideboard' in line.lower():
            in_side_deck = True
            continue
            
        # Check for placements
        rank_match = re.search(r'\b(1st|2nd|3rd|4th)(?:\s+place)?\b', line, re.IGNORECASE)
        if rank_match:
            if current_rank:
                placements.append({
                    "rank": current_rank,
                    "player": current_player or "Unknown",
                    "combos": current_combos
                })
            current_rank = rank_match.group(1).lower()
            current_combos = []
            in_side_deck = False
            
            # Extract player name
            player = re.sub(r'\b(1st|2nd|3rd|4th)(?:\s+place)?\b', '', line, flags=re.IGNORECASE)
            player = re.sub(r'^[\s:\-]+', '', player)
            if player:
                current_player = player.strip()
            else:
                current_player = "Unknown"
            continue
            
        if current_rank and not in_side_deck:
            if is_combo(line):
                current_combos.append(line)
                
    if current_rank:
        placements.append({
            "rank": current_rank,
            "player": current_player or "Unknown",
            "combos": current_combos
        })
        
    return placements

def main():
    data = json.load(open('extracted_data.json', encoding='utf-8'))
    
    # Load CSV to map exact link -> HTML
    rows = []
    with open('wbo_bbx_combos\wbo_bbx_combos_with_dates.csv', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
        
    patched_count = 0
    events_to_remove = []
    
    # Track which links from `links_to_patch` were found
    found_links = set()
    
    for e in data:
        link = e.get('link') or ''
        if link in links_to_patch or e.get('event_name') in links_to_patch:
            found_links.add(link or e.get('event_name'))
            
            # Find html in CSV (match on base URL to avoid hash mismatches)
            base_link = link.split('?')[0].split('#')[0]
            html_text = None
            for row in rows:
                if base_link in row[1] or base_link in row[3]:
                    html_text = row[4]
                    break
            
            # Special fallback for names without URL
            if not html_text:
                for row in rows:
                    if (e.get('event_name') or '') in str(row):
                        html_text = row[4]
                        break

            if html_text:
                extracted_placements = extract_combos_from_html(html_text)
                total_extracted = sum(len(p.get('combos', [])) for p in extracted_placements)
                
                if total_extracted > 0:
                    e['placements'] = extracted_placements
                    patched_count += 1
                else:
                    events_to_remove.append(e)
            else:
                events_to_remove.append(e)
                
    print(f"\nSummary:")
    print(f"Patched events: {patched_count}")
    print(f"Events to remove (image-only): {len(events_to_remove)}")
    print(f"Total processed: {patched_count + len(events_to_remove)} out of 46")
    
    final_data = [e for e in data if e not in events_to_remove]
    
    with open('extracted_data.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
        
if __name__ == '__main__':
    main()
