#!/usr/bin/env python
"""Translate JSON/CSV files using tab-separated translation mappings with field-specific sections."""

import sys
import json
import re
import pandas as pd
from pathlib import Path

def parse_mapping_file(mapping_file):
    """Parse mapping file with sections. Supports both --- FIELD --- and plain FIELD formats."""
    
    sections = {}
    current_section = None
    
    with open(mapping_file, 'r', encoding='utf-8') as f: 
        for line in f:
            line = line.strip()
            
            # Check for section header with --- delimiters
            if line.startswith('---') and '---' in line[3:]:
                # Extract section name between the --- markers
                end_marker = line.index('---', 3) + 3
                section_text = line[3:end_marker-3].strip()
                # Normalize: lowercase, remove spaces, handle plurals and special cases
                normalized = section_text.lower().replace(' ', '_').replace('-', '_')
                # Handle common variations
                if normalized == 'contexts':
                    normalized = 'context'
                elif normalized == 'questions':
                    normalized = 'question'
                elif normalized == 'parameters':
                    normalized = 'param'
                elif normalized == 'additional_context___bias':
                    normalized = 'additional_context_bias'
                elif normalized == 'additional_context___culture':
                    normalized = 'additional_context_culture'
                current_section = normalized
                sections[current_section] = []
            # Check for plain section header (no ---, just text followed by tab or end of line)
            # This must come AFTER checking for translation pairs to avoid false positives
            elif line and '\t' in line and current_section:
                # Parse translation pair
                parts = line.split('\t', 1)
                if len(parts) == 2 and not line.startswith('---'):
                    # Skip header rows like "Korean\tJapanese"
                    if parts[0].lower() not in ['korean', 'japanese', 'source', 'target', 'chinese', 'english']:
                        sections[current_section].append((parts[0], parts[1]))
            elif line and len(line) > 0:
                # Extract text before any tab (header might have trailing tab)
                header_text = line.split('\t')[0] if '\t' in line else line
                # Check if it's an ASCII uppercase header (not CJK text)
                is_ascii = all(ord(c) < 128 or c in ' -_' for c in header_text)
                is_uppercase = header_text.upper() == header_text
                has_lowercase = any(c.islower() for c in header_text)
                
                if is_ascii and is_uppercase and not has_lowercase and header_text.strip():
                    # This is a section header
                    section_text = header_text.strip()
                    normalized = section_text.lower().replace(' ', '_').replace('-', '_')
                    # Handle common variations
                    if normalized == 'contexts':
                        normalized = 'context'
                    elif normalized == 'questions':
                        normalized = 'question'
                    elif normalized == 'parameters':
                        normalized = 'param'
                    elif 'additional' in normalized and 'context' in normalized:
                        if 'bias' in normalized:
                            normalized = 'additional_context_bias'
                        elif 'culture' in normalized:
                            normalized = 'additional_context_culture'
                    current_section = normalized
                    sections[current_section] = []
    
    # Sort each section's replacements by length (longest first)
    for section in sections:
        sections[section].sort(key=lambda x: len(x[0]), reverse=True)
    
    return sections

def translate_json_file(data, sections):
    """Translate JSON data using field-specific mappings."""
    
    import uuid
    
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
                        # Use placeholder strategy to prevent partial re-replacement
                        temp_text = item
                        replacement_map = {}
                        
                        for source, target in replacements:
                            if source in temp_text:
                                # Create unique placeholder
                                placeholder = f"__PLACEHOLDER_{uuid.uuid4().hex}__"
                                replacement_map[placeholder] = target
                                temp_text = temp_text.replace(source, placeholder)
                                total_replacements += 1
                        
                        # Replace all placeholders with actual targets
                        for placeholder, target in replacement_map.items():
                            temp_text = temp_text.replace(placeholder, target)
                        
                        template[field_name][i] = temp_text
                        
                # Handle string fields
                elif isinstance(original_value, str):
                    temp_text = original_value
                    replacement_map = {}
                    
                    for source, target in replacements:
                        if source in temp_text:
                            # Create unique placeholder
                            placeholder = f"__PLACEHOLDER_{uuid.uuid4().hex}__"
                            replacement_map[placeholder] = target
                            temp_text = temp_text.replace(source, placeholder)
                            total_replacements += 1
                    
                    # Replace all placeholders with actual targets
                    for placeholder, target in replacement_map.items():
                        temp_text = temp_text.replace(placeholder, target)
                    
                    template[field_name] = temp_text
    
    return data, total_replacements

def translate_csv_file(df, sections):
    """Translate CSV data by applying section-specific replacements to matching columns."""
    
    import uuid
    
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
                # Process each row
                for idx in df.index:
                    if pd.isna(df.at[idx, col]):
                        continue
                    
                    temp_text = df.at[idx, col]
                    replacement_map = {}
                    
                    for source, target in replacements:
                        if source in temp_text:
                            # Create unique placeholder
                            placeholder = f"__PLACEHOLDER_{uuid.uuid4().hex}__"
                            replacement_map[placeholder] = target
                            temp_text = temp_text.replace(source, placeholder)
                            total_replacements += 1
                            section_counts[section_name] += 1
                    
                    # Replace all placeholders with actual targets
                    for placeholder, target in replacement_map.items():
                        temp_text = temp_text.replace(placeholder, target)
                    
                    df.at[idx, col] = temp_text
    
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