# Read the ko-jp.txt file with tab-separated Korean-Japanese translations
# Store as list of (before, after) tuples
replacements = []
with open('ko-jp.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and '\t' in line:
            parts = line.split('\t', 1)
            if len(parts) == 2:
                # Skip the line number prefix (e.g., "1. ")
                korean = parts[0].split('. ', 1)[1] if '. ' in parts[0] else parts[0]
                japanese = parts[1]
                replacements.append((korean, japanese))

# Sort replacements by length of the Korean string (longest first)
# This ensures longer phrases are matched before shorter substrings
replacements.sort(key=lambda x: len(x[0]), reverse=True)

# Read the JSON file as text
with open('data/raw/ko-ko_templates.json', 'r', encoding='utf-8') as f:
    json_text = f.read()

# Perform text replacements sequentially (longest strings first)
replacement_count = 0
for korean, japanese in replacements:
    # Escape the strings for JSON context (handle quotes and backslashes)
    # Need to handle escape characters properly:
    # 1. First escape backslashes (so \ becomes \\)
    # 2. Then escape quotes (so " becomes \")
    korean_escaped = korean.replace('\\', '\\\\').replace('"', '\\"')
    japanese_escaped = japanese.replace('\\', '\\\\').replace('"', '\\"')
    
    # Create the search pattern with quotes (as it appears in JSON)
    search_str = f'"{korean_escaped}"'
    replace_str = f'"{japanese_escaped}"'
    
    # Count and replace using exact string matching
    occurrences = json_text.count(search_str)
    if occurrences > 0:
        json_text = json_text.replace(search_str, replace_str)
        replacement_count += occurrences

# Save the translated JSON
with open('data/raw/ko-jp_templates.json', 'w', encoding='utf-8') as f:
    f.write(json_text)

print(f"Made {replacement_count} replacements from {len(replacements)} patterns")
print("Saved to data/raw/ko-jp_templates.json")