import json
import re

data = json.load(open('extracted_data.json', encoding='utf-8'))

junk_to_remove = [
    "2nd: Corj3",
    "2nd: Guzzy",
    "2nd: Modulus",
    "3-4th: Yushwa, M1key",
    "3rd: Nixus_VT",
    "3rd: Reinelia787",
    "3rd: Zore",
    "5-8th: Jakkthatonedude, CrownAxe, Phenominator, Wrenagayde",
    "Bits: Ball, rush, elevate, point",
    "Bits: Elevate, Hexa, Point, Under Needle",
    "Bits: low rush, ball, elevate",
    "Bounty Winner: (Drop Attack Battle Set) - Mel12",
    "Bounty Winner: (Gear Case White ver.) - Fireredx7964",
    "Bounty Winner: (Random Booster FoxBrush Select) - reddmatrixx",
    "Bounty Winner: (Random Booster Vol. 7) - Albus",
    "Bounty Winner: (Random Booster Vol. 8) - Firered",
    "Captain: AngeloDragoon",
    "Captain: Beyshredder13",
    "Captain: D/D Rezeal",
    "Captain: Exia",
    "Captain: JRF-TO",
    "Captain: KaydenChrys",
    "Captain: ZeY",
    "Captain: xenoseas",
    "FInals: 3on3",
    "Note: Used in Swiss & Grand",
    "Prize Money: $234.50 + Trophy",
    "Prize Money: $33.50",
    "Prize Money: $67.50",
    "Ratchets: 1-60, 3-60, 9-60, 7-60",
    "Ratchets: 4-60, 5-70, 3-60, 9-60",
    "Ratchets: 7-60, 5-70, 9-60, 5-60",
    "Stadium Used: Takara Tomy BX-10 Xtreme Stadium",
    "[b]4th Place: oldBenKenobi"
]

bounty_replacements = {
    "Bounty Winner: (Dranbrave S6-60V) - BLADERPN": "Dranbrave S6-60V",
    "Bounty Winner: (Dranstrike 4-50FF) - Rai22James": "Dranstrike 4-50FF",
    "Bounty Winner: (SamuraiCalibur 6-70M) - Christoff": "SamuraiCalibur 6-70M",
    "Bounty Winner: (SharkScale 4-50UF) - Blader ATC & Firered": "SharkScale 4-50UF",
    "Bounty Winner: (SharkScale 4-50UF) - Lio_blader": "SharkScale 4-50UF",
    "Bounty Winner: (Wolf Hunt F0-60DB / Gear Case White ver.) - Hackermans": "Wolf Hunt F0-60DB"
}

prefixes_to_strip = [
    "ACordz: ", "Ace Pokébey: ", "Bey1: ", "Bey2: ", "Bey3: ",
    "CloroxWipes: ", "CrisisCrusher07: ", "FishermanYon: ", "Gaven: ",
    "Helsgydja: ", "Junebuggarella: ", "Kabl: ", "Kamen Y: ", "LoloLegacy: ",
    "Mr pokee: ", "Oyapapi: ", "Rokki33: ", "SIDE: ", "Side Board: ",
    "Side deck: ", "Sideboard: ", "Sidedeck: ", "Used on on rounds 5 & 6: ",
    "bongobongo: ", "buicejox: ", "geetster99: ", "sword blader: "
]

fixed_count = 0
removed_count = 0

for e in data:
    for p in e.get('placements', []):
        combos = p.get('combos', [])
        new_combos = []
        for c in combos:
            if c in junk_to_remove:
                removed_count += 1
                continue
            
            if c in bounty_replacements:
                new_combos.append(bounty_replacements[c])
                fixed_count += 1
                continue
                
            if c == "5:80 orb":
                new_combos.append("5-80 orb")
                fixed_count += 1
                continue
                
            if c == "Keel Shark: 4-55Hexa":
                new_combos.append("Keel Shark 4-55Hexa")
                fixed_count += 1
                continue
                
            if c == "WhaleWave: 4-70Wedge":
                new_combos.append("WhaleWave 4-70Wedge")
                fixed_count += 1
                continue
            
            matched_prefix = False
            for prefix in prefixes_to_strip:
                if c.startswith(prefix):
                    new_combos.append(c[len(prefix):])
                    fixed_count += 1
                    matched_prefix = True
                    break
                    
            if not matched_prefix:
                new_combos.append(c)
                
        p['combos'] = new_combos

if fixed_count > 0 or removed_count > 0:
    json.dump(data, open('extracted_data.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f"Fixed {fixed_count} combos and removed {removed_count} junk strings.")
else:
    print("None found.")
