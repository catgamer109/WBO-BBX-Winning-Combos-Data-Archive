import json

c = json.load(open('compiled_challonge_stages.json', encoding='utf-8'))
w = json.load(open('wbo_parsed_events.json', encoding='utf-8'))

urls = {x['URL'].lower() for x in c[-30:] if x.get('URL')}
w_urls = []
for e in w[-40:]:
    links = e.get('Bracket link', [])
    if isinstance(links, str): links = [links]
    for l in links:
        w_urls.append(l.lower())

matches = [u for u in urls if any(u in wu for wu in w_urls)]
print('Matches:', len(matches))
print('URLs in c:', len(urls))
