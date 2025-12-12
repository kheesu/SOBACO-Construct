#!/usr/bin/env python
"""Command-line interface for SOBACO dataset generation."""

import argparse
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import LANGUAGES, GENERATED_DATA_DIR, RAW_DATA_DIR, get_names, get_idk_options
import itertools
import random
import ast


def _expand_csv_template(template_row, names, idk_options):
    """Expand a CSV template row into multiple dataset rows.
    
    CSV templates have:
    - {param} placeholders in context/additional_context
    - param field with pipe-delimited options (e.g., "车间|班组|工位")
    - Fixed options that need permutation
    - name1, name2 already specified
    """
    rows = []
    
    # Parse the param options
    param_field = template_row.get('param', '')
    if param_field and '|' in param_field:
        param_options = param_field.split('|')
    else:
        param_options = [param_field] if param_field else ['']
    
    # Get the fixed names from template
    name1 = template_row['name1']
    name2 = template_row['name2']
    
    # Parse options - they're in string tuple format like "('小张', '小李', '无法判断')"
    options_str = template_row['options']
    try:
        # Use ast.literal_eval to safely parse the string tuple
        original_options = ast.literal_eval(options_str)
    except:
        # Fallback parsing
        original_options = tuple(opt.strip().strip("'") for opt in options_str.strip("()").split(','))
    
    # For each param option
    for param in param_options:
        # Fill in the {param} placeholder
        context = template_row['context'].replace('{param}', param)
        additional_context = template_row['additional_context'].replace('{param}', param) if template_row.get('additional_context') else ''
        
        # Generate all permutations of options
        for options_perm in itertools.permutations(original_options):
            row = {
                'context': context,
                'additional_context': additional_context,
                'type': template_row['type'],
                'question': template_row['question'],
                'options': options_perm,
                'answer': template_row['answer'],
                'biased_option': template_row.get('biased_option', ''),
                'category': template_row['category'],
                'sample_idx': template_row['sample_idx'],
                'name1': name1,
                'name2': name2,
                'param': param
            }
            rows.append(row)
    
    return rows


def load_templates(language: str):
    """Load templates from JSON or CSV file for specified language."""
    template_map = {
        "ja": "ja_templates.json",
        "ja-ko": "ko_templates.json",
        "ja-zh": "zh_templates.json",
        "ko": "ko-ko_templates.json",
        "ko-jp": "ko-jp_templates.json",
        "ko-zh": "ko-zh_templates.json",
        "zh": "zh_standard_templates.json",
        "zh-csv": "c_sobaco_templates.csv",
        "zh-ja": "zh-ja_templates.json",
        "zh-ko": "zh-ko_templates.json"
    }
    
    if language not in template_map:
        return None
    
    template_file = RAW_DATA_DIR / template_map[language]
    
    if not template_file.exists():
        print(f"Error: Template file not found: {template_file}")
        return None
    
    try:
        # Check if it's a CSV file
        if template_file.suffix == '.csv':
            import pandas as pd
            df = pd.read_csv(template_file, encoding='utf-8')
            # Convert DataFrame to list of dicts
            templates = df.to_dict('records')
            return templates, 'csv'
        else:
            # JSON format
            with open(template_file, 'r', encoding='utf-8') as f:
                templates = json.load(f)
            return templates, 'json'
    except Exception as e:
        print(f"Error loading templates: {e}")
        return None


def generate_dataset(language: str, output: str = None):
    """Generate dataset for specified language."""
    print(f"Generating {language} dataset...")
    
    # Load templates
    result = load_templates(language)
    if result is None:
        print(f"Error: Could not load templates for language '{language}'")
        print(f"Supported languages: {', '.join(LANGUAGES)}")
        return
    
    templates, template_format = result
    
    # Get configuration for the language
    names = get_names(language)
    idk_options = get_idk_options(language)
    
    print(f"  Using names: {names}")
    print(f"  IDK options: {len(idk_options)} variants")
    print(f"  Templates: {len(templates)} total ({template_format} format)")
    
    import pandas as pd
    
    if template_format == 'csv':
        # CSV templates are already partially expanded
        print(f"  Expanding CSV templates...")
        all_rows = []
        for i, template_row in enumerate(templates, 1):
            if i % 20 == 0:
                print(f"    Processing template {i}/{len(templates)}...")
            all_rows.extend(_expand_csv_template(template_row, names, idk_options))
    else:
        # JSON templates need full generation
        from generator import _generate_rows
        print(f"  Generating rows...")
        all_rows = []
        for i, template in enumerate(templates, 1):
            if i % 10 == 0:
                print(f"    Processing template {i}/{len(templates)}...") 
            all_rows.extend(_generate_rows(template, names, idk_options))
    
    print(f"  Total rows generated: {len(all_rows)}")
    
    # Create DataFrame
    df = pd.DataFrame(all_rows)
    
    # Determine output path
    if output is None:
        output = GENERATED_DATA_DIR / f"{language}_dataset.csv"
    else:
        output = Path(output)
    
    # Ensure output directory exists
    output.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to CSV
    print(f"  Saving to: {output}")
    df.to_csv(output, index=False, encoding='utf-8')
    
    print(f"✓ Dataset generated successfully!")
    print(f"  Rows: {len(df)}")
    print(f"  Columns: {list(df.columns)}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SOBACO Dataset Constructor - Generate bias detection datasets"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate dataset")
    generate_parser.add_argument(
        "--language", "-l",
        choices=LANGUAGES,
        default="ja",
        help="Language to generate (default: ja)"
    )
    generate_parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file path"
    )
    
    # List command
    list_parser = subparsers.add_parser("list", help="List available templates")
    list_parser.add_argument(
        "--language", "-l",
        choices=LANGUAGES,
        help="Filter by language"
    )
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show repository information")
    
    args = parser.parse_args()
    
    if args.command == "generate":
        generate_dataset(args.language, args.output)
    elif args.command == "list":
        list_templates(args.language)
    elif args.command == "info":
        show_info()
    else:
        parser.print_help()


def list_templates(language: str = None):
    """List available templates with optional filtering."""
    print("Available templates:")
    print(f"  Filter - Language: {language or 'all'}")
    print()
    
    # Load templates from JSON files
    language_names = {
        "ja": "Japanese",
        "ja-ko": "Korean",
        "ja-zh": "Chinese"
    }
    
    for lang_code, lang_name in language_names.items():
        if language and language != lang_code:
            continue
        
        result = load_templates(lang_code)
        if result is None:
            print(f"{lang_name} ({lang_code}): Template file not found")
            continue
        
        templates, template_format = result
        print(f"{lang_name} ({lang_code}): {len(templates)} templates ({template_format})")
        print()


def show_info():
    """Show repository information."""
    from config import ROOT_DIR, DATA_DIR
    
    print("=" * 60)
    print("SOBACO Dataset Constructor")
    print("=" * 60)
    print()
    print("Configuration:")
    print(f"  Root directory: {ROOT_DIR}")
    print(f"  Data directory: {DATA_DIR}")
    print(f"  Raw data (templates): {RAW_DATA_DIR}")
    print(f"  Generated data: {GENERATED_DATA_DIR}")
    print()
    print("Supported languages:")
    for lang in LANGUAGES:
        names = get_names(lang)
        idk_count = len(get_idk_options(lang))
        result = load_templates(lang)
        if result:
            templates, template_format = result
            template_count = len(templates)
            status = "✓"
        else:
            template_count = 0
            template_format = "N/A"
            status = "✗"
        print(f"  {status} {lang}: {len(names)} names, {idk_count} IDK options, {template_count} templates ({template_format})")
    print()
    print("Template files:")
    template_files = list(RAW_DATA_DIR.glob("*.json"))
    for tf in sorted(template_files):
        print(f"  - {tf.name}")
    print("=" * 60)


if __name__ == "__main__":
    main()
