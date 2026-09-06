import json

junk = [
    "Shout out to all the staff, judges, sponsors, food vendors, and others!",
    "FreakyTendons HandyMannyPoQue Datboidoggo",
    "Check us out on YouTube and instagram @Gulfcoastbladers for updates and tournament highlights!",
    "did not remember to write theirs down.",
    "Wackocarnival86 Akuna VileVosskV",
    "Costume Contest Winner: Gumball2",
    "Event was small so I'm only including first place here",
    "3on3 First to 5 points First Stage | 6 Round",
    "Thank you everyone! See you again on the 13th",
    "Event was originally setup to be a ranked event but due to turnout was reduced to a unranked.",
    "But everyone went home safe and happily despite the snow.",
    "There was a tie for third but by request of Chamoy720 CoolClaw123 was declared third place.",
    "Player left before asking for combos.",
    "Due to an error with our deck recording system his deck was unable to be recorded for this post",
    "While using Rod, this balder had a staggering 100% win rate against Dragoon on elevate.",
    "These decks were used during both stages and no changes were made",
    "Mfw I didn't take a group photo...",
    "4/21/24 : Xtreme Beyblade Minnesota: Bring The Thunder!",
    "Only posting first place as it was only a tournament of 5 which I believe is OK",
    "Location: 340 Belleville Ave Belleville NJ",
    "Mcthunder Abracadabra @McLightning",
    "Thanks to Danileojar Serphus and SILVA⁰ for the help judging!",
    "Bey Dress Up Contest Winner: Aemeryn",
    "Wed. May 28 2025 • Houston, Texas",
    "Deck Format First to 7 points Finals Stage | Single Elimination",
    "Left (Dimthe3rd), Middle (MUSHYULTRA), Right"
]

data = json.load(open('extracted_data.json', encoding='utf-8'))
removed = 0
for e in data:
    for p in e.get('placements', []):
        combos = p.get('combos', [])
        new_combos = []
        for c in combos:
            if c in junk:
                continue
            new_combos.append(c)
            
        if len(new_combos) != len(combos):
            removed += (len(combos) - len(new_combos))
            p['combos'] = new_combos

if removed > 0:
    json.dump(data, open('extracted_data.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f"Removed {removed} junk sentences.")
else:
    print("None found.")
