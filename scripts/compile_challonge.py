import pandas as pd
import re
import json

def estimate_points(score_cluster):
    if pd.isna(score_cluster) or not isinstance(score_cluster, str):
        return None
    scores = re.findall(r'"scores":\[(\d+),\s*(\d+)\]', score_cluster)
    if not scores:
        return None
    
    winning_scores = []
    for s1, s2 in scores:
        s1, s2 = int(s1), int(s2)
        if s1 == 0 and s2 == 0:
            continue
        winning_scores.append(max(s1, s2))
    
    if not winning_scores:
        return None
    
    min_winning = min(winning_scores)
    
    if min_winning == 1:
        return "Quick advance"
    elif min_winning in [2, 3]:
        return f"Best of {min_winning*2-1}"
    else:
        return f"{min_winning} points"

def process():
    import sys
    import os
    
    append_mode = False
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        append_mode = True
    else:
        input_file = 'challonge_parsed/challonge-bulk-extractor-v7.csv'
        
    df = pd.read_csv(input_file)
    
    results = []
    
    for i, row in df.iterrows():
        url = row.get('web_scraper_start_url')
        if not isinstance(url, str):
            continue
            
        g_type = row.get('group_stage_type')
        f_type = row.get('final_stage_type')
        player_count = row.get('player_count')
        
        g_scores = row.get('group_stage_score_cluster')
        f_scores = row.get('final_stage_score_cluster')
        
        # If there is only a "final stage" listed then treat that as the group/first stage.
        if pd.isna(g_type) and not pd.isna(f_type):
            g_type = f_type
            f_type = None
            # Swap score clusters to match
            g_scores = f_scores
            f_scores = None
            
        first_points = estimate_points(g_scores)
        final_points = estimate_points(f_scores)
        
        results.append({
            'URL': url,
            'Player Count': int(player_count) if not pd.isna(player_count) else None,
            'First Stage Format': g_type if not pd.isna(g_type) else None,
            'Final Stage Format': f_type if not pd.isna(f_type) else None,
            'First Stage Points': first_points,
            'Final Stage Points': final_points
        })
        
    clean_records = []
    for r in results:
        clean_r = {}
        for k, v in r.items():
            if pd.isna(v):
                clean_r[k] = None
            else:
                clean_r[k] = v
        clean_records.append(clean_r)
        
    if append_mode and os.path.exists('compiled_challonge_stages.json'):
        with open('compiled_challonge_stages.json', 'r', encoding='utf-8') as f:
            existing_records = json.load(f)
        existing_records.extend(clean_records)
        final_records = existing_records
    else:
        final_records = clean_records
        
    out_df = pd.DataFrame(final_records)
    out_df.to_csv('compiled_challonge_stages.csv', index=False)
    
    with open('compiled_challonge_stages.json', 'w', encoding='utf-8') as f:
        json.dump(final_records, f, indent=2)
        
    print(f"Compiled {len(final_records)} tournaments to compiled_challonge_stages.csv and .json")

if __name__ == '__main__':
    process()