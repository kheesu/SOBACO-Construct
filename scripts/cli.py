#!/usr/bin/env python
"""Command-line interface for SOBACO dataset generation."""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import LANGUAGES, GENERATED_DATA_DIR
from templates import ja_templates, ko_templates


def generate_dataset(language: str, output: str = None):
    """Generate dataset for specified language."""
    print(f"Generating {language} dataset...")
    
    # Import generator
    from generator import construct
    
    # Select templates based on language
    if language == "ja":
        from templates.ja_templates import templates
    elif language == "ko":
        from templates.ko_templates import ko_templates as templates
    else:
        print(f"Error: Language '{language}' not supported")
        return
    
    # Generate dataset
    # TODO: Add generation logic here
    
    print(f"✓ Generated dataset for {language}")
    if output:
        print(f"✓ Saved to {output}")


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
        print(f"Available templates for {args.language or 'all languages'}:")
        # TODO: Implement listing
    elif args.command == "info":
        print("SOBACO Dataset Constructor")
        print(f"Supported languages: {', '.join(LANGUAGES)}")
        print(f"Data directory: {GENERATED_DATA_DIR}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
