#!/usr/bin/env python
"""Command-line interface for SOBACO dataset generation."""

import argparse
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import LANGUAGES, GENERATED_DATA_DIR, RAW_DATA_DIR, get_names, get_idk_options, CATEGORIES


def load_templates(language: str):
    """Load templates from JSON file for specified language."""
    template_map = {
        "ja": "ja_templates.json",
        "ja-ko": "ko_templates.json",
        "ja-zh": "zh_templates.json"
    }
    
    if language not in template_map:
        return None
    
    template_file = RAW_DATA_DIR / template_map[language]
    
    if not template_file.exists():
        print(f"Error: Template file not found: {template_file}")
        return None
    
    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            templates = json.load(f)
        return templates
    except Exception as e:
        print(f"Error loading templates: {e}")
        return None


def generate_dataset(language: str, output: str = None):
    """Generate dataset for specified language."""
    print(f"Generating {language} dataset...")
    
    # Load templates from JSON
    templates = load_templates(language)
    if templates is None:
        print(f"Error: Could not load templates for language '{language}'")
        print(f"Supported languages: {', '.join(LANGUAGES)}")
        return
    
    # Get configuration for the language
    names = get_names(language)
    idk_options = get_idk_options(language)
    
    print(f"  Using names: {names}")
    print(f"  IDK options: {len(idk_options)} variants")
    print(f"  Templates: {len(templates)} total")
    
    # Generate dataset
    # TODO: Add generation logic here
    
    # Determine output path
    if output is None:
        output = GENERATED_DATA_DIR / f"{language}_dataset.csv"
    else:
        output = Path(output)
    
    print(f"✓ Generated dataset for {language}")
    print(f"✓ Would save to {output}")


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
    list_parser.add_argument(
        "--category", "-c",
        choices=CATEGORIES,
        help="Filter by category"
    )
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show repository information")
    
    args = parser.parse_args()
    
    if args.command == "generate":
        generate_dataset(args.language, args.output)
    elif args.command == "list":
        list_templates(args.language, getattr(args, 'category', None))
    elif args.command == "info":
        show_info()
    else:
        parser.print_help()


def list_templates(language: str = None, category: str = None):
    """List available templates with optional filtering."""
    print("Available templates:")
    print(f"  Filter - Language: {language or 'all'}, Category: {category or 'all'}")
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
        
        templates = load_templates(lang_code)
        if templates is None:
            print(f"{lang_name} ({lang_code}): Template file not found")
            continue
            
        print(f"{lang_name} ({lang_code}): {len(templates)} templates")
        
        # Count by category
        category_counts = {}
        for template in templates:
            cat = template.get('category', 'unknown')
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        for cat, count in sorted(category_counts.items()):
            if category and category != cat:
                continue
            print(f"  - {cat}: {count} templates")
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
        templates = load_templates(lang)
        template_count = len(templates) if templates else 0
        status = "✓" if templates else "✗"
        print(f"  {status} {lang}: {len(names)} names, {idk_count} IDK options, {template_count} templates")
    print()
    print("Categories:")
    for cat in CATEGORIES:
        print(f"  - {cat}")
    print()
    print("Template files:")
    template_files = list(RAW_DATA_DIR.glob("*.json"))
    for tf in sorted(template_files):
        print(f"  - {tf.name}")
    print("=" * 60)


if __name__ == "__main__":
    main()
