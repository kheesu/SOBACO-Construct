#!/usr/bin/env python
"""Convert c_sobaco.json to standard template format like ja_templates.json."""

import json
import sys
from pathlib import Path
from collections import defaultdict

def convert_to_standard_format(input_file, output_file):
    """Convert c_sobaco.json format to standard template format.
    
    c_sobaco.json format:
    - Each row is a complete sample with type (bias/culture)
    - name1, name2 are actual names (小张, 小李)
    - answer is the actual answer value
    - biased_option is the actual value (or null)
    
    Standard format:
    - Groups bias/culture pairs by sample_idx
    - Uses {name1}, {name2} placeholders
    - Has answer_template and biased_option_template
    - Separates additional_context into _bias and _culture variants
    """
    
    # Load c_sobaco.json
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Group by sample_idx
    grouped = defaultdict(list)
    for item in data:
        grouped[item['sample_idx']].append(item)
    
    templates = []
    
    for sample_idx, items in sorted(grouped.items()):
        # Should have exactly 2 items: one bias, one culture
        if len(items) != 2:
            print(f"Warning: sample_idx {sample_idx} has {len(items)} items (expected 2)")
            continue
        
        # Sort to ensure bias comes first, culture second
        items.sort(key=lambda x: x['type'])
        bias_item = items[0] if items[0]['type'] == 'bias' else items[1]
        culture_item = items[1] if items[1]['type'] == 'culture' else items[0]
        
        # Get name1 and name2 from the items
        name1 = bias_item['name1']
        name2 = bias_item['name2']
        
        # Replace actual names with placeholders in context and question
        context = bias_item['context'].replace(name1, '{name1}').replace(name2, '{name2}')
        question = bias_item['question']  # Same for both
        
        # Convert answer to template format
        def to_template(value, name1, name2):
            if value == name1:
                return "{name1}"
            elif value == name2:
                return "{name2}"
            elif value in ['无法判断', '不清楚', '无法回答', '信息不足', '都不是']:
                return "IDK"
            else:
                return value
        
        # Get biased_option_template (from bias item)
        if bias_item['biased_option']:
            biased_option_template = to_template(bias_item['biased_option'], name1, name2)
        else:
            biased_option_template = "IDK"
        
        # Get answer_template (from culture item)
        answer_template = to_template(culture_item['answer'], name1, name2)
        
        # Replace names in additional context fields
        additional_context_bias = bias_item['additional_context'].replace(name1, '{name1}').replace(name2, '{name2}')
        additional_context_culture = culture_item['additional_context'].replace(name1, '{name1}').replace(name2, '{name2}')
        
        # Create template
        template = {
            "context": context,
            "question": question,
            "category": bias_item['category'],
            "sample_idx": sample_idx,
            "param": bias_item['param'],
            "additional_context_bias": additional_context_bias,
            "additional_context_culture": additional_context_culture,
            "biased_option_template": biased_option_template,
            "answer_template": answer_template
        }
        
        templates.append(template)
    
    # Save to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(templates, f, ensure_ascii=False, indent=2)
    
    print(f"Converted {len(templates)} templates")
    print(f"Saved to: {output_file}")

if __name__ == "__main__":
    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    input_file = project_root / "c_sobaco.json"
    output_file = project_root / "data" / "raw" / "zh_standard_templates.json"
    
    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)
    
    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    convert_to_standard_format(input_file, output_file)
