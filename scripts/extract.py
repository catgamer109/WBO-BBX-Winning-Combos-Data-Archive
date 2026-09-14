import pandas as pd
from bs4 import BeautifulSoup
import json
import re
import sys
import os

input_csv = sys.argv[1] if len(sys.argv) > 1 else 'wbo_bbx_combos_with_dates.csv'
output_json = 'compiled_data/extracted_data.json'

df = pd.read_csv(input_csv)

extracted_data = []

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def process_post(html_content, author, post_date):
    if pd.isna(html_content) or not str(html_content).strip():
        return
        
    if pd.isna(author):
        author = "NaN"
        
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove signatures
    for sig in soup.find_all('div', class_='post-signature'):
        sig.decompose()
        
    # Extract links before we modify the soup structure too much
    links = {}
    challonge_map = {}
    for a in soup.find_all('a'):
        href = a.get('href', '')
        text_clean = clean_text(a.get_text())
        if 'Thread-' in href and 'Winning-Combinations' not in href and 'The-WBO-Beyblade-X-Format' not in href:
            links[text_clean] = href
        elif 'challonge.com' in href:
            challonge_map[text_clean] = href
            
    # Replace block-level tags and <br> with newlines
    for hr in soup.find_all('hr'):
        hr.replace_with('\n---SPLIT---\n')
    for br in soup.find_all('br'):
        br.replace_with('\n')
    for block in soup.find_all(['div', 'p', 'hr', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
        if block.string:
            block.insert_before('\n')
            block.insert_after('\n')
        else:
            block.insert(0, '\n')
            block.append('\n')
            
    text_content = soup.get_text()
    lines = [clean_text(line) for line in text_content.split('\n') if clean_text(line)]
    
    events = []
    current_event = None
    current_placement = None
    in_optional_rules = False
    in_team_member_list = False
    
    def init_event(name, link_href):
        return {
            'event_name': name,
            'link': link_href,
            'author': author,
            'post_date': post_date,
            'event_date': None,
            'explicit_event_name': None,
            'event_page_link': None,
            'bracket_link': None,
            'ranked_status': None,
            'first_stage_format': None,
            'final_stage_format': None,
            'player_count': None,
            'placements': []
        }
    
    for line in lines:
        line_lower = line.lower()
        
        # Detect new event header
        is_event_header = False
        link_href = None
        for link_text, href in links.items():
            if link_text and link_text in line:
                is_event_header = True
                link_href = href
                break
                
        if is_event_header:
            if current_event and current_event.get('placements'):
                events.append(current_event)
            current_event = init_event(line, link_href)
            current_placement = None
            in_optional_rules = False
            continue
            
        if not current_event:
            current_event = init_event('Unknown Event', None)
            
        if line == '---SPLIT---':
            current_placement = None
            in_optional_rules = False
            in_team_member_list = False
            continue
            
        # Check for event-level meta fields
        meta_field_detected = False
        meta_key = None
        meta_val = None
        
        if line_lower.startswith('date:') or line_lower.startswith('event date:'):
            meta_field_detected = True; meta_key = 'event_date'; meta_val = line.split(':', 1)[1].strip()
        elif line_lower.startswith('event name:'):
            meta_field_detected = True; meta_key = 'explicit_event_name'; meta_val = line.split(':', 1)[1].strip()
        elif line_lower.startswith('event page link:'):
            val = line.split(':', 1)[1].strip()
            for k, v in links.items():
                if k and k in val:
                    val = v
                    break
            meta_field_detected = True; meta_key = 'event_page_link'; meta_val = val
        elif line_lower.startswith('bracket link:'):
            val = line.split(':', 1)[1].strip()
            for k, v in challonge_map.items():
                if k and k in val:
                    val = v
                    break
            meta_field_detected = True; meta_key = 'bracket_link'; meta_val = val
        elif line_lower in ('ranked', 'unranked', 'ranked/unranked') or line_lower.startswith('ranked ') or line_lower.startswith('unranked '):
            meta_field_detected = True; meta_key = 'ranked_status'; meta_val = line.strip()
        elif line_lower.startswith('first stage'):
            meta_field_detected = True; meta_key = 'first_stage_format'; meta_val = line.split(':', 1)[1].strip() if ':' in line else line
        elif line_lower.startswith('final stage'):
            meta_field_detected = True; meta_key = 'final_stage_format'; meta_val = line.split(':', 1)[1].strip() if ':' in line else line
        elif line_lower.startswith('player count:'):
            meta_field_detected = True; meta_key = 'player_count'; meta_val = line.split(':', 1)[1].strip()
            
        if meta_field_detected:
            if current_event and current_event.get('placements'):
                events.append(current_event)
                current_event = init_event('Unknown Event', None)
                current_placement = None
                
            current_event[meta_key] = meta_val
            in_team_member_list = False
            continue
            
        # Detect placement like "1st: Player" or "1st - Player" or "1."
        placement_match = re.match(r'^[^a-zA-Z0-9]*([1-8](?:st|nd|rd|th|ed|\.))(?:\s*place)?\b[:\-\s]*(.*)', line, re.IGNORECASE)
        if placement_match:
            if in_team_member_list:
                current_placement['combos'].append(line)
                continue
                
            rank = placement_match.group(1).lower()
            # Normalize misspellings
            rank = re.sub(r'1(?:th|ed|\.)$', '1st', rank)
            rank = re.sub(r'2(?:th|ed|\.)$', '2nd', rank)
            rank = re.sub(r'3(?:th|ed|\.)$', '3rd', rank)
            rank = re.sub(r'([4-8])(?:ed|st|nd|rd|\.)$', r'\1th', rank)
            
            player = placement_match.group(2).strip()
            player = re.sub(r'^@', '', player).strip()
            
            # If we see a 1st place and the current event already has placements, start a new event
            if rank == '1st' and current_event and current_event['placements']:
                events.append(current_event)
                current_event = init_event('Unknown Event', None)
                
            if rank in ('1st', '2nd', '3rd'):
                current_placement = {
                    'rank': rank,
                    'player': player,
                    'combos': []
                }
                current_event['placements'].append(current_placement)
            else:
                # 4th place and below are omitted
                current_placement = None
                
            in_optional_rules = False
            in_team_member_list = False
            continue
            
        # Inside placement -> it's a combo
        if current_placement and line:
            if 'click to view' in line_lower or 'top 3' in line_lower or 'image:' in line_lower:
                continue
            if re.match(r'^(group stage|finals?|final stage|first stage|winners? bracket|losers? bracket|top [0-9]+)\s*:?$', line_lower):
                continue
            if line.endswith(':') and len(line) < 30 and 'combo' not in line_lower:
                continue
                
            # Filter out random long comments (over 100 chars without a digit is likely a comment)
            if len(line) > 100:
                continue
                
            # Filter out common conversational phrases
            conversational_phrases = ['congrat', 'ggs', 'good game', 'shoutout', 'thanks', 'thank you', 'well played', 'good job']
            if any(phrase in line_lower for phrase in conversational_phrases) and not any(char.isdigit() for char in line):
                continue
                
            if not current_placement['player'] and len(line) < 30 and not '-' in line and not line_lower.startswith('winnings'):
                current_placement['player'] = line
                in_team_member_list = False
            else:
                current_placement['combos'].append(line)
                if line_lower.startswith('captain:'):
                    in_team_member_list = True
                else:
                    in_team_member_list = False
                
    if current_event and current_event.get('placements'):
        events.append(current_event)
        
    extracted_data.extend(events)

for _, row in df.iterrows():
    process_post(row['post-content'], row['author'], row['post-date'])

def clean_unicode(obj):
    if isinstance(obj, str):
        return obj.replace('\xa0', ' ').replace('\u200b', '').replace('\u200e', '').replace('\u200f', '')
    elif isinstance(obj, list):
        return [clean_unicode(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: clean_unicode(value) for key, value in obj.items()}
    return obj

extracted_data = clean_unicode(extracted_data)

if os.path.exists(output_json):
    with open(output_json, 'r', encoding='utf-8') as f:
        existing_data = json.load(f)
else:
    existing_data = []

existing_data.extend(extracted_data)

with open(output_json, 'w', encoding='utf-8') as f:
    json.dump(existing_data, f, indent=2, ensure_ascii=False)

print(f"Extracted {len(extracted_data)} new events.")
print(f"Total events now: {len(existing_data)}")
