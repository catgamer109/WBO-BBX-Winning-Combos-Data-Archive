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
    
    # Tournament Name
    title_tag = soup.find('title')
    if title_tag:
        data["Tournament name"] = title_tag.text.split(' - ')[0].strip()
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
    # Try explicit "Stadium" header first
    stadium_match_explicit = re.search(r'Stadiums?(?:\s*type)?\s*:?\s*\n([^\n]+)\n', text, re.IGNORECASE)
    if stadium_match_explicit and len(stadium_match_explicit.group(1).strip()) > 3:
        data["Stadium type"] = stadium_match_explicit.group(1).strip()
    else:
        stadium_match = re.search(r'([^.\n]*(?:xtreme stadium|stadium)[^.\n]*)', text, re.IGNORECASE)
        if stadium_match:
            snippet = stadium_match.group(1).strip()
            # Ensure it's not just the generic "Stadium type:" header without value
            if len(snippet) > 100:
                snippet = snippet[:100] + "..."
            if "stadium" in snippet.lower() and len(snippet) > 7:
                data["Stadium type"] = snippet

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
    # The custom format thing can literally be anything so figure out a plan for it
    # We look for "Tournament Rules" and the next line is usually the format.
    rules_match = re.search(r'Tournament Rules\n(.*?)\n', text)
    if rules_match:
        fmt = rules_match.group(1).strip()
        if fmt.lower() not in ["x format", "beyblade x"]:
            data["Custom format"] = fmt
            
    if data["Custom format"] == "NOT FOUND":
        custom_indicators = ['team format', 'x classic', 'custom format']
        for ci in custom_indicators:
            if ci in text.lower():
                data["Custom format"] = ci
                break
                
    # Optional Rules / Ranked Clauses
    optional_match = re.search(r'(?:Optional Rules|Special Rules|Additional Rules|Ranked Clause[s]?):?\s*\n(.*?)(?:\n\n|\n[A-Z][a-z]+)', text, re.IGNORECASE | re.DOTALL)
    if optional_match:
        rules_text = optional_match.group(1).strip()
        if rules_text:
            data["Optional rules"] = rules_text[:500]
            
    # First Stage Match Type Fallback
    if data["First Stage Settings"]["Match Type"] == "NOT FOUND":
        data["First Stage Settings"]["Match Type"] = "4-point"
        
    # Final Stage Fallbacks
    if data["Final Stage Settings"]["Bracket type"] == "NOT FOUND":
        data["Final Stage Settings"]["Bracket type"] = "single elimination"
    if data["Final Stage Settings"]["Battle Type"] == "NOT FOUND":
        data["Final Stage Settings"]["Battle Type"] = data["First Stage Settings"]["Battle Type"]
        
    if data["Final Stage Settings"]["Match Type"] == "NOT FOUND":
        try:
            date_str = data.get("Event date", "")
            if date_str and date_str != "NOT FOUND":
                event_date = dateutil.parser.parse(date_str, fuzzy=True)
                threshold_date = datetime(2025, 11, 26)
                if event_date < threshold_date:
                    data["Final Stage Settings"]["Match Type"] = "7-point"
                else:
                    data["Final Stage Settings"]["Match Type"] = data["First Stage Settings"]["Match Type"]
            else:
                data["Final Stage Settings"]["Match Type"] = data["First Stage Settings"]["Match Type"]
        except Exception:
            data["Final Stage Settings"]["Match Type"] = data["First Stage Settings"]["Match Type"]
        
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
