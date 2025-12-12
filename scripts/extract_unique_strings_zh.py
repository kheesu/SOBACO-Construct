#!/usr/bin/env python
"""Extract unique strings from zh_standard_templates.json in encounter order."""

import json
from pathlib import Path

def extract_unique_strings(input_file, output_file):
    """Extract unique strings from template file maintaining encounter order."""
    
    # Load the JSON file
    with open(input_file, 'r', encoding='utf-8') as f:
        templates = json.load(f)
    
    # Dictionaries to maintain order of first encounter
    unique_strings = {
        'context': [],
        'question': [],
        'param': [],
        'additional_context_bias': [],
        'additional_context_culture': [],
        'name': []
    }
    
    # Sets to track what we've seen
    seen = {key: set() for key in unique_strings.keys()}
    
    # Process each template
    for template in templates:
        # Context
        context = template.get('context', '')
        if context and context not in seen['context']:
            unique_strings['context'].append(context)
            seen['context'].add(context)
        
        # Question
        question = template.get('question', '')
        if question and question not in seen['question']:
            unique_strings['question'].append(question)
            seen['question'].add(question)
        
        # Parameters (can be a list)
        params = template.get('param', [])
        if isinstance(params, list):
            for param in params:
                if param and param not in seen['param']:
                    unique_strings['param'].append(param)
                    seen['param'].add(param)
        elif params and params not in seen['param']:
            unique_strings['param'].append(params)
            seen['param'].add(params)
        
        # Additional context bias (already has {name1} and {name2} placeholders in the template)
        bias = template.get('additional_context_bias', '')
        if bias and bias not in seen['additional_context_bias']:
            unique_strings['additional_context_bias'].append(bias)
            seen['additional_context_bias'].add(bias)
        
        # Additional context culture (already has {name1} and {name2} placeholders in the template)
        culture = template.get('additional_context_culture', '')
        if culture and culture not in seen['additional_context_culture']:
            unique_strings['additional_context_culture'].append(culture)
            seen['additional_context_culture'].add(culture)
    
    # Extract unique name placeholders (we know they're {name1} and {name2})
    unique_strings['name'] = ['{name1}', '{name2}']
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        for category, strings in unique_strings.items():
            f.write(f"=== {category.upper()} ===\n")
            for string in strings:
                f.write(f"{string}\n")
            f.write("\n")
    
    # Print summary
    print(f"Extracted unique strings from {input_file}")
    print(f"Results saved to {output_file}")
    print("\nSummary:")
    for category, strings in unique_strings.items():
        print(f"  {category}: {len(strings)} unique strings")
    print(f"\nTotal: {sum(len(strings) for strings in unique_strings.values())} unique strings")

if __name__ == "__main__":
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    input_file = project_root / "data" / "raw" / "zh_standard_templates.json"
    output_file = project_root / "data" / "raw" / "zh_unique_strings.txt"
    
    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        exit(1)
    
    extract_unique_strings(input_file, output_file)
