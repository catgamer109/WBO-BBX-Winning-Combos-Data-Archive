import re

all_links = set()
with open('multi_event_posts.md', 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('- **Links inside CSV HTML:**'):
            links_str = line.replace('- **Links inside CSV HTML:**', '').strip()
            if links_str not in ('None', '*Post not found in CSV.*'):
                links = [l.strip() for l in links_str.split(',')]
                for l in links:
                    if l:
                        all_links.add(l)

# write the one-liner to a file
with open('all_thread_links.txt', 'w', encoding='utf-8') as out:
    quoted_links = [f'"{link}"' for link in sorted(all_links)]
    out.write("[" + ",".join(quoted_links) + "]")

print(f"Collected {len(all_links)} unique links.")
