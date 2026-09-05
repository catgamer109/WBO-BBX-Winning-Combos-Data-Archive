import pandas as pd
import json
import re
import glob
import os
from bs4 import BeautifulSoup
import time

def extract_from_html(html, url, c_dict):
    if not isinstance(html, str):
        return None
        
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator='\n', strip=True)
    
    data = {
        "Tournament name": "NOT FOUND",
        "Location": "NOT FOUND",
        "Event date": "NOT FOUND",
        "Ranked or unranked": "Unranked",
        "Stadium type": "NOT FOUND",
        "Event thread link": url,
        "Bracket link": "NOT FOUND",
        "Player count": {"Actual attendees": "NOT FOUND"},
        "Optional rules": "NOT FOUND",
        "First Stage Settings": {"Bracket type": "NOT FOUND", "Battle Type": "NOT FOUND", "Match Type": "NOT FOUND"},
        "Final Stage Settings": {"Bracket type": "NOT FOUND", "Battle Type": "NOT FOUND", "Match Type": "NOT FOUND"},
        "Custom format": "NOT FOUND"
    }
    
    # Title & Location
    title_match = soup.find('title')
    if title_match:
        title = title_match.text.strip()
        if title.endswith(" - World Beyblade Organization"):
            title = title[:-len(" - World Beyblade Organization")]
            
        parts = title.split(" - ")
        if len(parts) > 1 and ',' in parts[-1]:
            data["Location"] = parts[-1].strip()
            title = " - ".join(parts[:-1])
            
        data["Tournament name"] = title.strip()
    else:
        h1_tag = soup.find('h1')
        if h1_tag:
            data["Tournament name"] = h1_tag.text.strip()
            
    # Event Date
    date_match = re.search(r'Date and Time\n(.*?)\n', text)
    if date_match:
        data["Event date"] = date_match.group(1).strip()
    else:
        date_fallback = re.search(r'(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\.\s+[A-Za-z]+\s+\d{1,2}(?:,\s+\d{4})?', text)
        if date_fallback:
            data["Event date"] = date_fallback.group(0).strip()
            
    # Ranked or Unranked
    text_flat = text.replace('\n', ' ').lower()
    ranked_indicators = ["ranked on the wbo global leaderboard", "part of the wbo rankings"]
    if any(ind in text_flat for ind in ranked_indicators) or "\nRanked\n" in text or "RankedBeyblade" in text:
        data["Ranked or unranked"] = "Ranked"
    else:
        data["Ranked or unranked"] = "Unranked"
        
    # Stadium Type
    stadium_match = re.search(r'((?:[A-Z][a-zA-Z0-9]* +)*[A-Z][a-zA-Z0-9]* +(?:Bey)?[Ss]tadium)\b', text)
    if stadium_match:
        match_text = stadium_match.group(1).strip()
        invalid_stadiums = [
            "a stadium",
            "the stadium",
            "p stadium",
            "match judges must disinfect stadium",
            "match judges should disinfect stadium"
        ]
        data["Stadium type"] = "NOT FOUND" if match_text.lower() in invalid_stadiums else match_text

    # Bracket link & Early Challonge Lookup
    challonge_links = []
    clean_links = []
    
    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'challonge.com' in href and 'rankings?' not in href:
            raw_href = href
            for suffix in ['/standings', '/participants', '/stations', '/settings', '/issues', '/groups']:
                if raw_href.endswith(suffix):
                    raw_href = raw_href[:-len(suffix)]
                    break
            if 'tournaments/signup/' in raw_href:
                raw_href = raw_href.replace('tournaments/signup/', '')
            challonge_links.append(raw_href)
            
            l = raw_href
            match = re.match(r'^(https?://[^/]+)(.*)$', l, re.IGNORECASE)
            if match: 
                l = match.group(1).lower() + match.group(2)
            if '#' in l: 
                l = l.split('#')[0]
            l = l.rstrip('/')
            clean_links.append(l.lower())
            
    if challonge_links:
        data["Bracket link"] = list(set(challonge_links))

    # Evaluate Challonge Data First
    first_fmt, final_fmt, first_pts, final_pts = None, None, None, None
    player_count = None
    found_c = [c_dict[l] for l in set(clean_links) if l in c_dict]
    
    if len(found_c) == 1:
        c = found_c[0]
        player_count = c.get('Player Count')
        if len(clean_links) > 1 and any(keyword in c['URL'].lower() for keyword in ['final', 'top', 'cut']):
            final_fmt = c['First Stage Format'] or c['Final Stage Format']
            final_pts = c['First Stage Points'] or c['Final Stage Points']
        else:
            first_fmt = c['First Stage Format']
            final_fmt = c['Final Stage Format']
            first_pts = c['First Stage Points']
            final_pts = c['Final Stage Points']
    elif len(found_c) > 1:
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
            first_c, final_c = None, None
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
                final_fmt = final_c['Final Stage Format'] or final_c['Final Stage Format']
                final_pts = final_c['Final Stage Points'] or final_c['Final Stage Points']

    # Apply Challonge Player Count
    if player_count is not None:
        data["Player count"]["Actual attendees"] = str(player_count)
    else:
        attendees_match = re.search(r'(?:Challengers|Going)\s*\(\s*(\d+)', text, re.IGNORECASE)
        if attendees_match:
            data["Player count"]["Actual attendees"] = attendees_match.group(1)
        
    # Format settings
    bracket_types = ['single elimination', 'double elimination', 'group round robin', 'group swiss', 'swiss', 'club format']
    battle_types = ['1on1', '3on3', '1 on 1', '3 on 3', '1-on-1', '3-on-3', 'deck', 'counter battle', 'p3c1', 'pick 3 choose 1']
    match_types = [r'4[- ]points?', r'5[- ]points?', r'7[- ]points?', 'best[- ]of[- ]3', r'first to \d+', r'\d+[- ]set wins?']
    
    def extract_settings(text_block):
        text_block = text_block.replace('\n', ' ').replace('\r', ' ')
        settings = {"Bracket type": "NOT FOUND", "Battle Type": "NOT FOUND", "Match Type": "NOT FOUND"}
        for bt in bracket_types:
            if re.search(r'\b' + bt + r'\b', text_block, re.IGNORECASE):
                settings["Bracket type"] = bt
                break
        for bt in battle_types:
            if re.search(r'\b' + bt + r'\b', text_block, re.IGNORECASE):
                val = bt
                if val in ['1 on 1', '1-on-1']: val = '1on1'
                if val in ['3 on 3', '3-on-3']: val = '3on3'
                settings["Battle Type"] = val
                break
        for mt in match_types:
            mt_match = re.search(r'\b' + mt + r'\b', text_block, re.IGNORECASE)
            if mt_match:
                val = mt_match.group(0).lower()
                if "set win" in val:
                    wins = int(re.search(r'\d+', val).group(0))
                    if wins > 1:
                        val = f"best of {wins * 2 - 1}"
                settings["Match Type"] = val
                break
        return settings

    # Text Block Isolation
    first_stage_matches = list(re.finditer(r'\b(?:First Stage|Group Stage)\b\s*[:\n][^\w]*((?:(?!(?:Final Stage|Finals)).){0,150})', text, re.IGNORECASE | re.DOTALL))
    final_stage_matches = list(re.finditer(r'\b(?:Final Stage|Finals)\b\s*[:\n][^\w]*(.{0,150})', text, re.IGNORECASE | re.DOTALL))
    
    fs_text = " ".join(m.group(1) for m in first_stage_matches)
    if not fs_text:
        rules_match_block = re.search(r'Tournament Rules(.*?)(?:Event Staff|Contact Organizer|$)', text, re.IGNORECASE | re.DOTALL)
        if rules_match_block:
            fs_text = rules_match_block.group(1)
            
    if not fs_text:
        fs_text = text
        
    data["First Stage Settings"] = extract_settings(fs_text)
    
    fallback_settings = extract_settings(text)
    for key in ["Bracket type", "Battle Type", "Match Type"]:
        if data["First Stage Settings"][key] == "NOT FOUND":
            data["First Stage Settings"][key] = fallback_settings[key]
    
    if final_stage_matches:
        fn_text = " ".join(m.group(1) for m in final_stage_matches)
        data["Final Stage Settings"] = extract_settings(fn_text)
        
    # APPLY CHALLONGE OVERRIDES HERE
    if first_fmt: data["First Stage Settings"]["Bracket type"] = first_fmt
    if first_pts: data["First Stage Settings"]["Match Type"] = first_pts
    if final_fmt: data["Final Stage Settings"]["Bracket type"] = final_fmt
    if final_pts: data["Final Stage Settings"]["Match Type"] = final_pts

    # Custom Format Aggressive Parsing
    if data["Ranked or unranked"] == "Unranked":
        data["Custom format"] = "NOT FOUND"
        text_lower = text.lower()
        name_lower = data["Tournament name"].lower()
        
        # 1. Explicit WBO alternate formats
        if 'x limited' in name_lower or text_lower.count('x limited') > 1 or re.search(r'\b(limited format|limited legal)\b', text_lower):
            data["Custom format"] = "X Limited"
        elif 'x classic' in name_lower or text_lower.count('x classic') > 1 or 'classic format' in text_lower:
            data["Custom format"] = "X Classic"
        elif 'x legacy' in name_lower or text_lower.count('x legacy') > 1 or re.search(r'\b(legacy format|legacy legal)\b', text_lower):
            data["Custom format"] = "X Legacy"
        elif 'team' in name_lower or 'team format' in text_lower or 'team tournament' in text_lower or text_lower.count('team battle') > 1:
            data["Custom format"] = "Team format"
        else:
            headers_to_skip = [
                "format", "event format", "tournament format", "format overview", 
                "quick format info", "need-to-know information", "additional information", 
                "event information", "contact information", "rules", "tournament rules",
                "registration information", "banner by", "note", "notes", "overview"
            ]
            
            boilerplate_phrases = [
                "x format", "standard format", "bbx format", "beyblade x format", 
                "x standard", "wbo standard", "wbo x format", "standard rules",
                "metal needle", "mn bit", "ranked season", "evolving ban", "banned for the rest of the season",
                "please read", "in addition to", "as over finish", "forgot", "what's the ban",
                "this tournament will be played", "format rulebook", "swiss", "elimination",
                "legal combinations", "format for this event", "format: x", "elxgsl bx format", 
                "elxgsl unlimited format", "elxgsl cx format", "pure skill", "pm me if",
                "join our", "cap(", "world beyblade organization", "for any questions",
                "we want this format", "this event is", "hi! one of the regulars", "banner by"
            ]
            
            garbage_patterns = [
                r'registration information', r'additional information', r'tournament information',
                r'event information', r'contact information', r'format info', r'rules',
                r'banner by', r'see more details', r'please read', r'pm me if', r'join our',
                r'cap\(', r'delta-red', r'crewcabanger', r'savanabanana',
                r'banachobroly', r'bananaboyguyboo', r'the evil legends', r'the elxgsl',
                r'the dallas beyblade association', r'world beyblade organization',
                r'for any questions', r'we want this format', r'in addition to', r'due to potential',
                r'as an event', r'this event is', r'more rules information', r'read through',
                r'click the', r'join the', r'participants', r'tournament format cap'
            ]
            
            for line in text.split('\n'):
                line_clean = line.strip()
                line_lower = line_clean.lower()
                
                if len(line_clean) < 15 or "http" in line_lower or "<" in line_clean:
                    continue
                    
                if line_clean in ["DeltaRedBandit", "SuperBanther", "Blading Bandit", "Crewcabanger", "Savanabanana", "BanchoBroly", "Bananaboyguyboo", "BankaiBlader"]:
                    continue
                    
                header_check = re.sub(r'[^a-z\s\-]', '', line_lower).strip()
                if header_check in headers_to_skip or len(header_check) < 5:
                    continue
                    
                is_garbage = False
                for pat in garbage_patterns:
                    if re.search(pat, line_lower):
                        is_garbage = True
                        break
                if is_garbage:
                    continue
                    
                if "format" in line_lower or "ban" in line_lower or "banned" in line_lower:
                    if "?" in line_lower: continue
                    
                    if re.search(r'(format is|playing the) (3on3|3 on 3|3v3|3 vs3|1on1|1v1|5on5|5v5|deck)', line_lower): continue
                    if re.search(r'(3on3|3 on 3|3v3|3 vs3|1on1|1v1|5on5|5v5|deck) format', line_lower): continue
                    if "3on3, best of 3 format" in line_lower or "3-on-3 format" in line_lower: continue
                    
                    if not any(bp in line_lower for bp in boilerplate_phrases):
                        if "banlist" in line_lower or "ban list" in line_lower or "restricted list" in line_lower or "banned" in line_lower:
                            data["Custom format"] = "Ban List"
                        else:
                            if len(line_clean) > 100:
                                data["Custom format"] = line_clean[:100] + "..."
                            else:
                                data["Custom format"] = line_clean
                        break
                                        
    # Optional Rules / Ranked Clauses
    predefined_optional_rules = [
        "Registered deck list", "Registered side deck", "Own finish", "Out-of-bounds finish",
        "Painted blades allowed", "Reveal and reorder", "Swap positions after battle",
        "Loser selects position after battle", "No disassembled components",
        "MN (Metal Needle) bit unbanned", "Metal Needle bit unbanned", "Adjust before presenting", 
        "No reverse", "3-second reverse countdown", "Out-of-Bounds ruled as Over Finish",
        "Decorated Parts Prohibition", "Battle Limit and Consecutive Draws Removal"
    ]
    
    found_predefined = []
    text_lower_full = text.lower()
    for pr in predefined_optional_rules:
        if pr.lower() in text_lower_full:
            found_predefined.append(pr)
            
    if found_predefined:
        data["Optional rules"] = ', '.join(found_predefined)[:500]
    else:
        data["Optional rules"] = "NOT FOUND"
        
    final_bracket_exists = data["Final Stage Settings"]["Bracket type"] != "NOT FOUND"
    final_match_exists = data["Final Stage Settings"]["Match Type"] != "NOT FOUND"
    
    if final_bracket_exists or final_match_exists:
        if data["Final Stage Settings"]["Battle Type"] == "NOT FOUND":
            data["Final Stage Settings"]["Battle Type"] = data["First Stage Settings"]["Battle Type"]
        
    return data

def main():
    csv_dir = r"e:\beyblade app\WBO-BBX-Winning-Combos-Data-Archive\event-threads\beyblade X events"
    csv_files = glob.glob(os.path.join(csv_dir, "*.csv"))
    
    try:
        with open('compiled_challonge_stages.json', 'r', encoding='utf-8') as f:
            challonge_data = json.load(f)
        c_dict = {c['URL'].lower(): c for c in challonge_data}
    except FileNotFoundError:
        print("compiled_challonge_stages.json not found. Proceeding without it.")
        c_dict = {}

    all_data = []
    
    print(f"Found {len(csv_files)} CSV files. Starting processing...")
    start_time = time.time()
    
    for f in csv_files:
        print(f"Reading {os.path.basename(f)}...")
        try:
            df = pd.read_csv(f)
            print(f"Processing {len(df)} rows in {os.path.basename(f)}...")
            for idx, row in df.iterrows():
                html = row.get('full-page-html')
                url = row.get('web_scraper_start_url')
                if html:
                    parsed = extract_from_html(html, url, c_dict)
                    if parsed:
                        all_data.append(parsed)
                        
                if idx % 1000 == 0 and idx > 0:
                    print(f"  ...processed {idx} rows")
        except Exception as e:
            print(f"Error reading {f}: {e}")
                    
    output_file = 'wbo_parsed_events.json'
    print(f"Finished processing. Writing {len(all_data)} records to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as out_f:
        json.dump(all_data, out_f, indent=2, ensure_ascii=False)
        
    end_time = time.time()
    print(f"Done in {end_time - start_time:.2f} seconds!")

if __name__ == "__main__":
    main()