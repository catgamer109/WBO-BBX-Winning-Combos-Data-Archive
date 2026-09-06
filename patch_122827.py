import json

data = json.load(open('extracted_data.json', encoding='utf-8'))

correct_placements = [
  {
    "rank": "1st",
    "player": "pikachugamemstr",
    "combos": [
      "Hover Wyvern 9-60K",
      "CobaltDragoon 5-60E",
      "WizardRod 1-60H"
    ]
  },
  {
    "rank": "2nd",
    "player": "FinalAvenger",
    "combos": [
      "MeteorDragoon 7-60L",
      "WizardRod 1-60B",
      "Hover Wyvern 9-60LR"
    ]
  },
  {
    "rank": "3rd",
    "player": "MikelStealsWifi",
    "combos": [
      "Hover Wyvern 9-60K",
      "FoxBrush H1-60R",
      "MeteorDragoon 3-70Z"
    ]
  }
]

fixed = False
for e in data:
    if "122827" in (e.get('link') or ""):
        e["placements"] = correct_placements
        # Also clean up the event name
        e["event_name"] = "Waffles and enthusiasm first event of 2026"
        e["event_date"] = "1/18/2026"
        e["stadium"] = "Takara Tomy BX-10 Xtreme Stadium"
        e["first_stage_format"] = "3 on 3 Swiss Bo1 first to 5pts"
        e["final_stage_format"] = "3 on 3 Single elimination Bo1 first to 7pts"
        fixed = True
        break

if fixed:
    json.dump(data, open('extracted_data.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print("Successfully patched event 122827.")
else:
    print("Event not found.")
