#!/usr/bin/env python
"""Translate JSON/CSV files using tab-separated translation mappings with field-specific sections."""

import sys
import json
import re
import pandas as pd
from pathlib import Path

def parse_mapping_file(mapping_file):
    """Parse mapping file with sections like --- FIELD_NAME ---."""
    
    sections = {}
    current_section = None
    
    with open(mapping_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Check for section header (may have content after ---, like "--- CONTEXT ---\t한국어 번역")
            if line.startswith('---') and '---' in line[3:]:
                # Extract section name between the --- markers
                end_marker = line.index('---', 3) + 3
                section_text = line[3:end_marker-3].strip()
                current_section = section_text.lower()
                sections[current_section] = []
            elif line and '\t' in line and current_section:
                # Parse translation pair
                parts = line.split('\t', 1)
                if len(parts) == 2 and not line.startswith('---'):
                    # Skip lines that look like headers (e.g., "source\ttarget" column names)
                    sections[current_section].append((parts[0], parts[1]))
    
    # Sort each section's replacements by length (longest first)
    for section in sections:
        sections[section].sort(key=lambda x: len(x[0]), reverse=True)
    
    return sections

def translate_json_file(data, sections):
    """Translate JSON data using field-specific mappings."""
    
    total_replacements = 0
    
    # Process each template in the JSON
    for template in data:
        for field_name, replacements in sections.items():
            # Check if this field exists in the template
            if field_name in template and template[field_name]:
                original_value = template[field_name]
                
                # Handle list fields (like param)
                if isinstance(original_value, list):
                    for i, item in enumerate(original_value):
                        for source, target in replacements:
                            if source in item:
                                template[field_name][i] = item.replace(source, target)
                                total_replacements += 1
                # Handle string fields
                elif isinstance(original_value, str):
                    for source, target in replacements:
                        if source in original_value:
                            template[field_name] = template[field_name].replace(source, target)
                            total_replacements += 1
    
    return data, total_replacements

def translate_csv_file(df, sections):
    """Translate CSV data by applying section-specific replacements to matching columns."""
    
    total_replacements = 0
    section_counts = {}
    
    # Map section names to CSV column names
    # CSV columns are flattened versions of JSON fields
    section_to_columns = {
        'context': ['context'],
        'question': ['question'],
        'param': ['param'],
        'additional_context_bias': ['additional_context'],  # Merged in CSV
        'additional_context_culture': ['additional_context'],  # Merged in CSV
        'options': ['options'],
    }
    
    # Process each section and its target columns
    for section_name, replacements in sections.items():
        # Get the columns this section should apply to
        target_columns = section_to_columns.get(section_name, [])
        
        if not target_columns:
            continue
        
        section_counts[section_name] = 0
        
        # Apply replacements to target columns only
        for col in target_columns:
            if col in df.columns and df[col].dtype == 'object':
                for source, target in replacements:
                    # Count replacements in this column
                    mask = df[col].str.contains(source, regex=False, na=False)
                    count = mask.sum()
                    if count > 0:
                        df[col] = df[col].str.replace(source, target, regex=False)
                        total_replacements += count
                        section_counts[section_name] += count
    
    return df, total_replacements, section_counts

def translate_file(mapping_file, input_file, output_file):
    """Translate a JSON or CSV file using field-specific mappings."""
    
    # Parse the mapping file into sections
    sections = parse_mapping_file(mapping_file)
    
    if not sections:
        print("No sections found in mapping file. Using default behavior.")
        print("Mapping file should have sections like: --- CONTEXT ---")
        return
    
    input_path = Path(input_file)
    file_extension = input_path.suffix.lower()
    
    if file_extension == '.json':
        # Load and translate JSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        data, total_replacements = translate_json_file(data, sections)
        
        # Save the translated JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"Made {total_replacements} replacements across {len(sections)} sections")
        for section, replacements in sections.items():
            print(f"  {section}: {len(replacements)} patterns")
    
    elif file_extension == '.csv':
        # Load and translate CSV file
        df = pd.read_csv(input_file, encoding='utf-8')
        
        df, total_replacements, section_counts = translate_csv_file(df, sections)
        
        # Save the translated CSV
        df.to_csv(output_file, index=False, encoding='utf-8')
        
        print(f"Made {total_replacements} replacements across {len([s for s in section_counts.values() if s > 0])} sections")
        for section, count in section_counts.items():
            if count > 0:
                print(f"  {section}: {count} replacements")
        print(f"Processed {len(df)} rows")
    
    else:
        print(f"Unsupported file format: {file_extension}")
        print("Supported formats: .json, .csv")
        return
    
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python translate.py <mapping_file> <input_file> <output_file>")
        print("\nExample:")
        print("  python translate.py ko-zh.txt data/raw/ko-ko_templates.json data/raw/ko-zh_templates.json")
        sys.exit(1)
    
    mapping_file = Path(sys.argv[1])
    input_file = Path(sys.argv[2])
    output_file = Path(sys.argv[3])
    
    if not mapping_file.exists():
        print(f"Error: Mapping file not found: {mapping_file}")
        sys.exit(1)
    
    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)
    
    translate_file(mapping_file, input_file, output_file)