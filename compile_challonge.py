import pandas as pd
import re
import json

def estimate_points(score_cluster):
    if pd.isna(score_cluster) or not isinstance(score_cluster, str):
        return None
    scores = re.findall(r'"scores":\[(\d+),\s*(\d+)\]', score_cluster)
    if not scores:
        return None
    max_score = 0
    for s1, s2 in scores:
        max_score = max(max_score, int(s1), int(s2))
    
    if max_score == 0:
        return None
    elif max_score == 1:
        return "Quick advance"
    elif max_score in [2, 3]:
        return f"{max_score} pts (or BO{max_score*2-1})"
    elif max_score in [4, 5, 6]:
        return "4 pts"
    elif max_score >= 7:
        return "7 pts"
    return str(max_score)

def process():
    df = pd.read_csv('challonge_parsed/challonge-bulk-extractor-v7.csv')
    
    results = []
    
    for i, row in df.iterrows():
        url = row.get('web_scraper_start_url')
        if not isinstance(url, str):
            continue
            
        g_type = row.get('group_stage_type')
        f_type = row.get('final_stage_type')
        
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
            'First Stage Format': g_type if not pd.isna(g_type) else None,
            'Final Stage Format': f_type if not pd.isna(f_type) else None,
            'First Stage Points': first_points,
            'Final Stage Points': final_points
        })
        
    out_df = pd.DataFrame(results)
    out_df.to_csv('compiled_challonge_stages.csv', index=False)
    
    # Save a clean JSON
    clean_records = []
    for r in results:
        clean_r = {}
        for k, v in r.items():
            if pd.isna(v):
                clean_r[k] = None
            else:
                clean_r[k] = v
        clean_records.append(clean_r)
        
    with open('compiled_challonge_stages.json', 'w', encoding='utf-8') as f:
        json.dump(clean_records, f, indent=2)
        
    print(f"Compiled {len(out_df)} tournaments to compiled_challonge_stages.csv and .json")

if __name__ == '__main__':
    process()
