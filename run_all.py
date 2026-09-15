import os
import subprocess
import shutil

csv_dir = "wbo_bbx_combos"
csvs = [
    "wbo_bbx_combos_with_dates.csv",
    "wbo_bbx_combos_with_dates-156.csv",
    "wbo_bbx_combos_with_dates_page155-156.csv",
    "wbo_bbx_combos_with_dates_page156-157.csv"
]

output = "compiled_data/extracted_data.json"
if os.path.exists(output):
    os.remove(output)

for csv in csvs:
    print(f"Extracting {csv}...")
    subprocess.run(["python", "scripts/extract.py", os.path.join(csv_dir, csv)])

# The clean scripts expect extracted_data.json in the root
root_json = "extracted_data.json"
shutil.copy(output, root_json)

# Run cleaning scripts
cleaning_scripts = [
    "clean_players.py",
    "remove_junk.py",
    "remove_junk2.py",
    "remove_junk3.py",
    "remove_junk4.py",
    "remove_junk5.py",
    "remove_junk6.py",
    "clean_colons.py",
    "clean_dashes.py",
    "remove_urls.py",
    "clean_tags.py",
    "clean_mangled.py",
    "clean_challonge.py",
    "purge_zerog.py",
    "fix_truncated.py",
    "patch_122827.py",
    "patch_missing_events.py"
]

# Run from root
for script in cleaning_scripts:
    script_path = f"scripts/{script}"
    if os.path.exists(script_path):
        print(f"Running {script}...")
        subprocess.run(["python", script_path])

# Move back to compiled_data
shutil.move(root_json, output)

# Run post-processing scripts that read from compiled_data
post_scripts = [
    "merge_metadata.py",
    "sync_databases.py"
]

for script in post_scripts:
    script_path = f"scripts/{script}"
    if os.path.exists(script_path):
        print(f"Running {script}...")
        subprocess.run(["python", script_path])
