import json

def remove_custom_format_field(json_filepath):
    # Load the parsed events JSON file
    with open(json_filepath, 'r', encoding='utf-8') as f:
        events = json.load(f)

    updated_count = 0

    for e in events:
        # Check if 'Custom format' key exists in the event dictionary and remove it
        if "Optional rules" in e:
            del e["Optional rules"]
            updated_count += 1

    # Save the updated dataset back to the file
    with open(json_filepath, 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)

    print(f"Successfully removed 'Custom format' from {updated_count} events in {json_filepath}")

if __name__ == "__main__":
    remove_custom_format_field('wbo_parsed_events.json')