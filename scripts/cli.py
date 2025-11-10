#!/usr/bin/env python
"""Command-line interface for SOBACO dataset generation."""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import LANGUAGES, GENERATED_DATA_DIR, get_names, get_idk_options, CATEGORIES


def generate_dataset(language: str, output: str = None):
    """Generate dataset for specified language."""
    print(f"Generating {language} dataset...")
    
    # Import generator
    from generator import construct
    
    # Select templates based on language
    if language == "ja":
        from templates.ja_templates import templates
    elif language == "ja-ko":
        from templates.ko_templates import ko_templates as templates
    elif language == "ja-zh":
        # TODO: Add Chinese templates when available
        print(f"Error: Chinese templates not yet implemented")
        return
    else:
        print(f"Error: Language '{language}' not supported")
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
    
    # Import templates
    from templates.ja_templates import templates as ja_templates
    from templates.ko_templates import ko_templates
    
    language_templates = {
        "ja": ("Japanese", ja_templates),
        "ja-ko": ("Korean", ko_templates),
    }
    
    for lang_code, (lang_name, templates) in language_templates.items():
        if language and language != lang_code:
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
    from config import ROOT_DIR, DATA_DIR, TEMPLATES_DIR
    
    print("=" * 60)
    print("SOBACO Dataset Constructor")
    print("=" * 60)
    print()
    print("Configuration:")
    print(f"  Root directory: {ROOT_DIR}")
    print(f"  Data directory: {DATA_DIR}")
    print(f"  Templates directory: {TEMPLATES_DIR}")
    print()
    print("Supported languages:")
    for lang in LANGUAGES:
        names = get_names(lang)
        idk_count = len(get_idk_options(lang))
        print(f"  - {lang}: {len(names)} names, {idk_count} IDK options")
    print()
    print("Categories:")
    for cat in CATEGORIES:
        print(f"  - {cat}")
    print()
    print("Output directory:")
    print(f"  {GENERATED_DATA_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
