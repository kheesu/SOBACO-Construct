# SOBACO Dataset Constructor

This project constructs and generates templates for the SOBACO (Social Bias and Cultural Commonsense) dataset proposed in the paper "Bias Mitigation or Cultural Commonsense? Evaluating LLMs with a Japanese Dataset".

## Table of Contents

- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Overview](#overview)
- [How It Works](#how-it-works)
- [Usage](#usage)
- [Multi-Language Support](#-multi-language-support)
- [Development](#-development)
- [Migration Guide](#-migration-guide)
- [Common Tasks](#-common-tasks)
- [Troubleshooting](#-troubleshooting)
- [Paper Reference](#paper-reference)

## 🚀 Quick Start

### Installation

Using UV (recommended):
```bash
uv sync
```

Using pip:
```bash
pip install -e .
```

### Generate Datasets

```bash
# Japanese dataset
python scripts/cli.py generate -l ja

# Korean dataset
python scripts/cli.py generate -l ko

# With custom output
python scripts/cli.py generate -l ja -o data/generated/custom.csv

# Show repository info
python scripts/cli.py info
```

## 📁 Project Structure

```
constructor/
├── src/                          # Source code
│   ├── __init__.py              # Package initialization
│   ├── config.py                # Configuration settings
│   ├── generator.py             # Dataset generation logic
│   └── templates/               # Template definitions
│       ├── __init__.py
│       ├── ja_templates.py      # Japanese templates (66 templates)
│       └── ko_templates.py      # Korean templates (66 templates)
├── data/                        # Data files
│   ├── raw/                     # Raw template exports and translation files
│   │   ├── ja_templates.json
│   │   ├── ko_templates.json
│   │   ├── zh_templates.json
│   │   └── jp_translate.csv
│   └── generated/               # Generated datasets
│       ├── ja_dataset.csv
│       ├── ko_dataset.csv
│       └── zh_dataset.csv
├── scripts/                     # Utility scripts
│   ├── cli.py                   # Command-line interface
│   └── translate.py             # Translation utilities
├── pyproject.toml              # Project configuration
└── README.md                   # This file
```

## Overview

SOBACO (Social Bias and Cultural Commonsense) is a dataset designed to evaluate how well Large Language Models distinguish between stereotypical biases and legitimate cultural commonsense reasoning. This repository provides the template construction system to generate the dataset in multiple languages.

### Dataset Description

According to Appendix C of the paper, each template populates the dataset by 36, 72, or 108 samples, depending on the number of parameters (context types) in the expressions:

- **36 samples**: Templates without parameters (base templates)
- **72 samples**: Templates with 2 parameter variations
- **108 samples**: Templates with 3 parameter variations

### Template Structure

Each of the 66 templates contains:
- **`context`**: Base context with placeholders `{name1}`, `{name2}`, and `{param}`
- **`question`**: The question to be answered
- **`category`**: Category (e.g., `hierarchical_relationship`, `gender`, `age`)
- **`sample_idx`**: Template index (1-66)
- **`param`**: List of parameter variations (empty list if no parameters)
- **`additional_context_bias`**: Additional context that introduces stereotypical bias
- **`additional_context_culture`**: Additional context with legitimate cultural information
- **`biased_option_template`**: Expected biased answer template
- **`answer_template`**: Correct answer template

### Key Files

- **`src/templates/ja_templates.py`**: 66 Japanese templates
- **`src/templates/ko_templates.py`**: 66 Korean templates  
- **`src/generator.py`**: Dataset generation logic
- **`src/config.py`**: Configuration (names, languages, paths)
- **`data/raw/*.json`**: Pre-exported template JSON files
- **`data/generated/*.csv`**: Generated dataset files

## How It Works

The construction process creates dataset samples through systematic permutations:

1. **Name Permutations**: Uses 3 names (佐藤, 鈴木, 田中 for Japanese / 김, 이, 박 for Korean) in all 2-permutation combinations (6 total)
2. **Context Types**: Generates both 'bias' and 'culture' variants (2 types)
3. **Option Shuffling**: Creates all permutations of answer choices (6 orderings)
4. **Parameter Variations**: If template has parameters, repeats for each parameter value

**Formula**: `6 (name pairs) × 2 (types) × 6 (option permutations) × N (params) = 36N samples per template`

- No parameters: 36 samples
- 2 parameters: 72 samples  
- 3 parameters: 108 samples

### Generated Fields

Each generated sample contains:
- `context`: The base scenario
- `additional_context`: Either bias or culture context
- `type`: 'bias' or 'culture'
- `question`: The question being asked
- `options`: Tuple of 3 answer choices (name1, name2, IDK variant)
- `answer`: Correct answer (IDK for bias type, culturally informed answer for culture type)
- `biased_option`: The stereotypical/biased answer (only for bias type)
- `category`: Question category
- `sample_idx`: Original template index
- `name1`, `name2`: Names used
- `param`: Parameter value used (or None)

## Usage

### Command-Line Interface

```bash
# Generate datasets
python scripts/cli.py generate -l ja           # Japanese
python scripts/cli.py generate -l ko           # Korean
python scripts/cli.py generate -l zh           # Chinese

# Custom output location
python scripts/cli.py generate -l ja -o data/generated/custom.csv

# Show repository information
python scripts/cli.py info

# List available templates
python scripts/cli.py list
```

### Use as a Python Module

```python
from src.templates import ja_templates, ko_templates
from src.config import LANGUAGES, NAMES, get_names
from src.generator import construct

# Get names for a language
names = get_names('ja')  # ['佐藤', '鈴木', '田中']

# Generate data for a single template
data = construct(ja_templates[0])

# Access configuration
print(LANGUAGES)  # ['ja', 'ko', 'zh']
```

### Export Templates to JSON

Templates are pre-exported in `data/raw/`. To regenerate:

```bash
# Export Japanese templates
python src/templates/ja_templates.py

# Export Korean templates
python src/templates/ko_templates.py
```

### Translation Workflow

Use the translation script to apply bulk replacements from a CSV file:

```bash
python scripts/translate.py
```

CSV format: 3 columns (target, replacement1, replacement2). The script generates two output files with each replacement applied.

## Requirements

- **Python** >= 3.12
- **pandas** >= 2.3.3

### Installation Options

```bash
# Using UV (recommended)
uv sync

# Using pip
pip install -e .

# Install just pandas
pip install pandas
```

## ✨ Key Features

- ✅ **Multi-Language Support**: Japanese, Korean, and Chinese templates
- ✅ **Bias vs Culture Distinction**: Each template generates both biased and culturally informed contexts
- ✅ **Systematic Coverage**: Exhaustive permutations ensure comprehensive evaluation
- ✅ **Reproducibility**: Fixed random seed (42) for consistent "I don't know" option selection
- ✅ **Modern Package Management**: Uses UV for fast, reliable dependency management
- ✅ **Pre-exported Templates**: JSON files included for easy integration
- ✅ **Organized Structure**: Clean separation of source, data, and scripts
- ✅ **CLI Interface**: Command-line tools for common tasks

## 🔧 Development

### Adding New Templates

1. Edit `src/templates/ja_templates.py` or `ko_templates.py`
2. Follow the existing template structure
3. Add template to the `templates` or `ko_templates` list
4. Regenerate datasets

### Adding a New Language

1. **Create template file**: `src/templates/XX_templates.py`
2. **Update config** (`src/config.py`):
   ```python
   LANGUAGES = ["ja", "ko", "zh", "XX"]  # Add language code
   NAMES["XX"] = ['Name1', 'Name2', 'Name3']  # Add names
   IDK_OPTIONS["XX"] = ['IDK1', 'IDK2', ...]  # Add IDK options
   ```
3. **Update template package** (`src/templates/__init__.py`):
   ```python
   from .XX_templates import XX_templates
   __all__ = [..., "XX_templates"]
   ```
4. **Generate and test** the new dataset

### Project Organization Benefits

- **Clear Separation**: Source code in `src/`, data in `data/`, scripts in `scripts/`
- **Easy Navigation**: Logical directory hierarchy with consistent naming
- **Scalability**: Simple to add new languages, templates, or features
- **Maintainability**: Related files grouped together, centralized configuration
- **Professional**: Follows Python packaging best practices

### Recommended Improvements

1. **Add Unit Tests**: Create `tests/` directory with pytest
2. **Add Type Hints**: Use mypy for static type checking
3. **Improve CLI**: Add progress bars, verbose mode, validation commands
4. **Add Documentation**: API docs, template creation guide, examples
5. **CI/CD Pipeline**: GitHub Actions for automated testing and linting
6. **Convert to YAML**: Move template data to YAML files for easier editing

## 🔄 Migration Guide

If you have existing code using the old structure:

### Old Import Paths ❌
```python
from templates import templates
from ko_template import ko_templates
import main
```

### New Import Paths ✅
```python
from src.templates import ja_templates, ko_templates
from src.config import LANGUAGES, NAMES
from src.generator import construct
```

### File Location Changes

| Old Location | New Location |
|-------------|--------------|
| `templates.py` | `src/templates/ja_templates.py` |
| `ko_template.py` | `src/templates/ko_templates.py` |
| `main.py` | `src/generator.py` |
| `templates.json` | `data/raw/ja_templates.json` |
| `dataset.csv` | `data/generated/ja_dataset.csv` |

All original files preserved in new locations. No data or functionality lost.

## 📋 Common Tasks

### Export Templates
```bash
python src/templates/ja_templates.py  # Creates data/raw/ja_templates.json
python src/templates/ko_templates.py  # Creates data/raw/ko_templates.json
```

### Generate Datasets
```bash
python scripts/cli.py generate -l ja  # Japanese
python scripts/cli.py generate -l ko  # Korean  
```

### Apply Translations
```bash
# Prepare CSV: target, replacement1, replacement2
python scripts/translate.py
```

### Check Configuration
```python
from src.config import LANGUAGES, NAMES, IDK_OPTIONS
print(f"Languages: {LANGUAGES}")
print(f"Japanese names: {NAMES['ja']}")
```

## 🆘 Troubleshooting

### Import Errors
**Problem**: `ModuleNotFoundError: No module named 'templates'`  
**Solution**: Update import paths to use new structure:
```python
from src.templates import ja_templates
```

### Can't Find Files
**Problem**: Files not in expected locations  
**Solution**: Check new locations:
- Templates: `src/templates/`
- Raw data: `data/raw/`
- Generated data: `data/generated/`
- Scripts: `scripts/`

### CLI Not Working
**Problem**: `python cli.py` fails  
**Solution**: Run from project root with full path:
```bash
python scripts/cli.py generate -l ja
```

### UTF-8 Encoding Errors
**Problem**: `UnicodeEncodeError` when exporting JSON  
**Solution**: Already fixed! All file operations now use `encoding='utf-8'`

## 🌐 Translation Notes

Several Japanese culture-specific templates had to be rewritten in order to make the dataset effective for Korean culture.

In the original dataset, "3歳と7歳の時に七五三のお祝いをした。" was used.
Since in Korea, there is no comparable event to 七五三, all-women's highschool and all-men's highschool was used.

Simillarly, "ひな祭り" was used for women-specific event for the Japanese templates. Since there is no comparable event in modern Korean culture, we had to change it to "명절 음식 준비" (lit. preparation of holiday dishes) for an event only experienced by women.

Sentences including "振袖" was changed to use "노리개" (decorative charm traditionally worn by women in Korea) instead, since there is no specific word for Korean traditional clothes that only women wears. Some cultural subtleties are lost, since "振袖" is usually only worn by unwed women (according to a Japanese-Korean Dictionary) and "노리개" is worn by both wed and unwed women in Korea. Just using "여성용 한복" (lit. Women's Hanbok) was considered, but including the word "women" in the query would most likely render the question meaningless so "노리개" was chosen instead.

DV was used in some of the templates, which was translated to "데이트폭력."
Since DV includes domestic violence between married couples, it does not translate 100%, but it was the closest word that is in common use in the Korean language.

"鯉のぼり" was used as an event for male children. Since there is no gender-specific events during childhood in Korea, mandatory military service was used to create the cultural context for the Korean template.

Unlike Japan, Korean people do not change their family name upon marriage, so all templates including the cultural context of changing their family name had to be changed. Until recently, it was culturally expected of the bride to prepare the furniture and home appliances, and the groom to prepare the residence. Therefore all template regarding name-changing was changed to "혼수마련" to test the cultural background of the bride preparing the furniture.

### Potential Improvements

In the original dataset, all parties were referred to as their family name (`{name1}さん`), as is typical in Japanese culture. However, when directly translated to Korean (`{name1}씨`), this does not feel very natural as it is not a very common way to refer to people in Korean culture. For now, it is left as-is, since we don't consider it to affect the end result too much, and to maintain as much one-to-one comparison to the original Japanese dataset as possible. But to make the text feel more natural, replacing the family name with the entire name (`김씨` -> `김희수`) or just using the first name (`김씨` -> `희수`) is an option.

## 📄 License

Please refer to the original SOBACO dataset paper and repository for licensing information.

## 🤝 Contributing

Contributions are welcome! Please ensure:
- New templates follow the existing structure
- Cultural adaptations are well-documented
- Code follows project conventions
- Tests pass (when implemented)

## Paper Reference

For more information about the SOBACO dataset and its evaluation methodology, please refer to the original paper:
"Bias Mitigation or Cultural Commonsense? Evaluating LLMs with a Japanese Dataset"