#!/usr/bin/env python
"""Fix zh_standard_templates.json by replacing names in additional_context fields."""

import json
from pathlib import Path
import pandas as pd

def fix_zh_templates(template_file, csv_file):
    """Fix the zh_standard_templates.json by replacing names with placeholders."""
    
    # Load the current templates
    with open(template_file, 'r', encoding='utf-8') as f:
        templates = json.load(f)
    
    # Load the CSV to get the original name mappings
    csv_df = pd.read_csv(csv_file, encoding='utf-8')
    
    # Create a mapping of sample_idx + type to the row data
    csv_map = {}
    for _, row in csv_df.iterrows():
        key = (row['sample_idx'], row['type'])
        csv_map[key] = row
    
    # Process each template
    for template in templates:
        sample_idx = template['sample_idx']
        
        # Get the bias and culture rows from CSV
        bias_row = csv_map.get((sample_idx, 'bias'))
        culture_row = csv_map.get((sample_idx, 'culture'))
        
        if bias_row is not None and culture_row is not None:
            name1 = bias_row['name1']
            name2 = bias_row['name2']
            
            # Replace names in additional_context_bias
            if 'additional_context_bias' in template:
                template['additional_context_bias'] = template['additional_context_bias'].replace(name1, '{name1}').replace(name2, '{name2}')
            
            # Replace names in additional_context_culture
            if 'additional_context_culture' in template:
                template['additional_context_culture'] = template['additional_context_culture'].replace(name1, '{name1}').replace(name2, '{name2}')
    
    # Save the fixed templates
    with open(template_file, 'w', encoding='utf-8') as f:
        json.dump(templates, f, ensure_ascii=False, indent=2)
    
    print(f"Fixed {len(templates)} templates")
    print(f"Updated: {template_file}")

if __name__ == "__main__":
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    template_file = project_root / "data" / "raw" / "zh_standard_templates.json"
    csv_file = project_root / "data" / "raw" / "c_sobaco_templates.csv"
    
    if not template_file.exists():
        print(f"Error: Template file not found: {template_file}")
        exit(1)
    
    if not csv_file.exists():
        print(f"Error: CSV file not found: {csv_file}")
        exit(1)
    
    fix_zh_templates(template_file, csv_file)
