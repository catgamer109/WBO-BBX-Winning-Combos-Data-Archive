import json

def fix_events():
    with open('extracted_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # We will remove all events that are related to these two tournaments
    # identifying them by the presence of 'MaxD' or 'Mia Kaub' as 1st place 
    # combined with 'Koii-Boy' as an author or player.
    
    new_data = []
    removed_count = 0
    for e in data:
        is_target = False
        placements = e.get('placements', [])
        if len(placements) >= 3:
            p1 = placements[0].get('player', '')
            p2 = placements[1].get('player', '')
            if (p1 == 'MaxD' and p2 == 'whynowhy') or (p1 == 'Mia Kaub' and p2 == 'Koii-Boy'):
                is_target = True
                
        if is_target:
            removed_count += 1
        else:
            new_data.append(e)
            
    print(f"Removed {removed_count} mangled/duplicate events.")
    
    # Insert the correct two events
    event_shogun = {
      "event_name": "TEAM ANDROMEDA PRESTENTS: SHOGUN SMACKDOWN",
      "link": "https://worldbeyblade.org/Thread-TEAM-ANDROMEDA-PRESTENTS-SHOGUN-SMACKDOWN-SCRANTON-PA-S-FIRST-BEYTOURNAMENT--118162",
      "author": "Koii-Boy",
      "post_date": "Jan. 16, 2026 7:10 PM",
      "event_date": "31/05/2025",
      "explicit_event_name": None,
      "event_page_link": "https://worldbeyblade.org/Thread-TEAM-ANDROMEDA-PRESTENTS-SHOGUN-SMACKDOWN-SCRANTON-PA-S-FIRST-BEYTOURNAMENT--118162",
      "bracket_link": "Bracket not available",
      "ranked_status": "UNRANKED",
      "stadium": "Xtreme Stadium (TAKARA TOMY)",
      "first_stage_format": "3on3; Double Elimination (First to 5)",
      "final_stage_format": "3on3; Single Elimination (First to 7)",
      "player_count": "6",
      "optional_rules": [],
      "placements": [
        {
          "rank": "1st",
          "player": "Mia Kaub",
          "combos": [
            "ShinobiKnife 7-70Level (First Stage & Final Stage)",
            "KnightShield 3-70Disk Ball (First Stage & Final Stage)",
            "WizardRod 3-60Ball (First Stage & Final Stage)"
          ]
        },
        {
          "rank": "2nd",
          "player": "Koii-Boy",
          "combos": [
            "SamuraiSaber 0-70Hexa (First Stage & Final Stage)",
            "ScorpioSpear 3-60Orb (First Stage & Final Stage)",
            "CobaltDragoon 1-60Elevate (First Stage & Final Stage)"
          ]
        },
        {
          "rank": "3rd",
          "player": "Kamen-C",
          "combos": [
            "CobaltDragoon 5-60Level (First Stage & Final Stage)",
            "WizardRod 9-60Free Ball (First Stage & Final Stage)",
            "TyrannoBeat 7-60Rush (First Stage & Final Stage)"
          ]
        }
      ]
    }
    
    event_double = {
      "event_name": "TEAM ANDROMEDA PRESTENTS: DOUBLE X-TREME: ENTER THE SCORPIONS DEN",
      "link": "https://worldbeyblade.org/Thread-TEAM-ANDROMEDA-PRESTENTS-DOUBLE-X-TREME-Enter-the-Scorpions-den--119481",
      "author": "Koii-Boy",
      "post_date": "Jan. 16, 2026 7:10 PM",
      "event_date": "09/08/2025",
      "explicit_event_name": None,
      "event_page_link": "https://worldbeyblade.org/Thread-TEAM-ANDROMEDA-PRESTENTS-DOUBLE-X-TREME-Enter-the-Scorpions-den--119481",
      "bracket_link": "Bracket not available",
      "ranked_status": "UNRANKED",
      "stadium": "Double Xtreme Stadium",
      "first_stage_format": "3on3; Double Elimination (First to 5)",
      "final_stage_format": "3on3; Double Elimination (First to 7)",
      "player_count": "7",
      "optional_rules": [],
      "placements": [
        {
          "rank": "1st",
          "player": "MaxD",
          "combos": [
            "WizardRod 5-60Ball (First Stage & Final Stage)",
            "SilverWolf 1-60Free Ball (First Stage & Final Stage)",
            "SharkEdge 3-60Low Rush (First Stage & Final Stage)"
          ]
        },
        {
          "rank": "2nd",
          "player": "whynowhy",
          "combos": [
            "WizardRod 3-60Level (First Stage & Final Stage)",
            "SharkEdge 1-60Low Flat (First Stage & Final Stage)",
            "PhoenixWing 9-60Point (First Stage & Final Stage)"
          ]
        },
        {
          "rank": "3rd",
          "player": "Koii-Boy",
          "combos": [
            "SamuraiSaber 0-70Hexa (First Stage & Final Stage)",
            "ScorpioSpear 3-60Low Orb (First Stage & Final Stage)",
            "CobaltDragoon 1-60Elevate (First Stage & Final Stage)"
          ]
        }
      ]
    }
    
    new_data.append(event_shogun)
    new_data.append(event_double)
    
    with open('extracted_data.json', 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)
        
    print("Successfully inserted the two clean events.")

if __name__ == '__main__':
    fix_events()
