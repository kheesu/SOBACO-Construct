import json
import csv

# Read the CSV file with replacements (3 columns: target, replacement1, replacement2)
replacements1 = {}
replacements2 = {}
with open('jp_translate.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) >= 3:
            target = row[0]
            replacement1 = row[1]
            replacement2 = row[2]
            replacements1[target] = replacement1
            replacements2[target] = replacement2

# Read the JSON file
with open('template.json', 'r', encoding='utf-8') as f:
    templates = json.load(f)

# Perform replacements in all string fields
def replace_in_template(template_obj, replacements):
    """Recursively replace text in template object."""
    if isinstance(template_obj, dict):
        return {k: replace_in_template(v, replacements) for k, v in template_obj.items()}
    elif isinstance(template_obj, list):
        return [replace_in_template(item, replacements) for item in template_obj]
    elif isinstance(template_obj, str):
        # Apply all replacements to this string
        result = template_obj
        for target, replacement in replacements.items():
            result = result.replace(target, replacement)
        return result
    else:
        return template_obj

# Apply first set of replacements
templates_updated1 = replace_in_template(templates, replacements1)

# Apply second set of replacements
templates_updated2 = replace_in_template(templates, replacements2)

# Save the first updated JSON
with open('template_replacement1.json', 'w', encoding='utf-8') as f:
    json.dump(templates_updated1, f, ensure_ascii=False, indent=4)

# Save the second updated JSON
with open('template_replacement2.json', 'w', encoding='utf-8') as f:
    json.dump(templates_updated2, f, ensure_ascii=False, indent=4)

print(f"Replaced {len(replacements1)} patterns")
print("Saved to template_replacement1.json and template_replacement2.json")