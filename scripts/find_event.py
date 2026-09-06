import pandas as pd
import glob
import os

csv_dir = r"e:\beyblade app\WBO-BBX-Winning-Combos-Data-Archive\event-threads\beyblade X events"
csv_files = glob.glob(os.path.join(csv_dir, "*.csv"))

for f in csv_files:
    df = pd.read_csv(f)
    for idx, row in df.iterrows():
        html = str(row.get('full-page-html', ''))
        if "ELXGSL SEASON 1 FINALE" in html:
            with open('scratch_elxgsl.html', 'w', encoding='utf-8') as out_f:
                out_f.write(html)
            print("Found and dumped to scratch_elxgsl.html")
            exit(0)
