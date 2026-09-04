import pandas as pd
import json
import re
import glob
import os
from bs4 import BeautifulSoup
from datetime import datetime
import dateutil.parser
import time

def extract_from_html(html, url):
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
        "Player count": {"Actual attendees": "NOT FOUND", "Cap": "NOT FOUND"},
        "Optional rules": "NOT FOUND",
        "First Stage Settings": {"Bracket type": "NOT FOUND", "Battle Type": "NOT FOUND", "Match Type": "NOT FOUND"},
        "Final Stage Settings": {"Bracket type": "NOT FOUND", "Battle Type": "NOT FOUND", "Match Type": "NOT FOUND"},
        "Custom format": "NOT FOUND"
    }
    
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
    # Known stadium names always end with the word "Stadium" or "Beystadium" and are proper nouns
    stadium_match = re.search(r'((?:[A-Z][a-zA-Z0-9]* +)*[A-Z][a-zA-Z0-9]* +(?:Bey)?[Ss]tadium)\b', text)
    if stadium_match:
        data["Stadium type"] = stadium_match.group(1).strip()
    else:
        data["Stadium type"] = "NOT FOUND"

    # Bracket link
    challonge_links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'challonge.com' in href and 'rankings?' not in href:
            for suffix in ['/standings', '/participants', '/stations', '/settings', '/issues', '/groups']:
                if href.endswith(suffix):
                    href = href[:-len(suffix)]
                    break
            if 'tournaments/signup/' in href:
                href = href.replace('tournaments/signup/', '')
            challonge_links.append(href)
            
    if challonge_links:
        data["Bracket link"] = list(set(challonge_links))
        
    # Player count (Cap & Attendees)
    cap_match = re.search(r'(\d+)\s+(?:player[s]?|participant[s]?)\s*(?:participation)?\s*(?:cap|limit)', text, re.IGNORECASE)
    if cap_match:
        data["Player count"]["Cap"] = cap_match.group(1)
    else:
        cap_match2 = re.search(r'(?:cap(?:ped)?|limit|participant limit)(?:\s*at\s*|:\s*|\s*is\s*)?(\d+)', text, re.IGNORECASE)
        if cap_match2:
            data["Player count"]["Cap"] = cap_match2.group(1)
            
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

    # Try to extract settings by searching for First Stage and Final Stage separately
    # Take the last match to prefer the detailed text body over the short header widget
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
    
    # If explicit mentions or Tournament Rules block failed to find anything, try parsing the whole text
    fallback_settings = extract_settings(text)
    for key in ["Bracket type", "Battle Type", "Match Type"]:
        if data["First Stage Settings"][key] == "NOT FOUND":
            data["First Stage Settings"][key] = fallback_settings[key]
    
    if final_stage_matches:
        fn_text = " ".join(m.group(1) for m in final_stage_matches)
        data["Final Stage Settings"] = extract_settings(fn_text)
        
    # Custom Format
    if data["Ranked or unranked"] == "Unranked":
        # The custom format thing can literally be anything so figure out a plan for it
        # We look for "Tournament Rules" and the next line is usually the format.
        rules_match = re.search(r'Tournament Rules\n(.*?)\n', text)
        benign_formats = [
            "x format", "beyblade x", "standard format", "bbx format", "beyblade x format", 
            "metal needle bit ban", "swiss format", "single elimination format", 
            "double elimination format", "round robin format", "deck format", 
            "1on1 format", "3on3 format", "group format", "banlist reminder",
            "ranked clause", "optional rule", "format information"
        ]
        if rules_match:
            fmt = rules_match.group(1).strip()
            if fmt.lower() not in benign_formats:
                data["Custom format"] = fmt
                
        if data["Custom format"] == "NOT FOUND" or data["Custom format"].lower() in benign_formats:
            data["Custom format"] = "NOT FOUND"
            
            text_lower = text.lower()
            name_lower = data["Tournament name"].lower()
            if 'x limited' in name_lower or text_lower.count('x limited') > 1 or re.search(r'\b(limited format|limited legal)\b', text_lower):
                data["Custom format"] = "X Limited"
            elif 'x classic' in name_lower or text_lower.count('x classic') > 1 or 'classic format' in text_lower:
                data["Custom format"] = "X Classic"
            elif 'x legacy' in name_lower or text_lower.count('x legacy') > 1 or re.search(r'\b(legacy format|legacy legal)\b', text_lower):
                data["Custom format"] = "X Legacy"
            elif 'team' in name_lower or 'team format' in text_lower or 'team tournament' in text_lower or text_lower.count('team battle') > 1:
                data["Custom format"] = "Team format"
                
            if data["Custom format"] == "NOT FOUND":
                for line in text.split('\n'):
                    line_lower = line.lower()
                    if re.search(r'\b(banlist|ban)\b', line_lower):
                        has_benign = False
                        for ex in benign_formats:
                            if ex in line_lower:
                                has_benign = True
                                break
                        if not has_benign:
                            clean_line = line.strip()
                            if len(clean_line) > 100:
                                data["Custom format"] = clean_line[:100] + "..."
                            else:
                                data["Custom format"] = clean_line
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
        
    if data["Final Stage Settings"]["Battle Type"] == "NOT FOUND":
        data["Final Stage Settings"]["Battle Type"] = data["First Stage Settings"]["Battle Type"]
        
    return data

def main():
    csv_dir = r"e:\beyblade app\WBO-BBX-Winning-Combos-Data-Archive\event-threads\beyblade X events"
    csv_files = glob.glob(os.path.join(csv_dir, "*.csv"))
    
    all_data = []
    
    print(f"Found {len(csv_files)} CSV files. Starting processing...")
    start_time = time.time()
    
    for f in csv_files:
        print(f"Reading {os.path.basename(f)}...")
        try:
            # We don't limit nrows now
            df = pd.read_csv(f)
            print(f"Processing {len(df)} rows in {os.path.basename(f)}...")
            for idx, row in df.iterrows():
                html = row.get('full-page-html')
                url = row.get('web_scraper_start_url')
                if html:
                    parsed = extract_from_html(html, url)
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
