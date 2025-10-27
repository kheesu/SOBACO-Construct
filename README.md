# SOBACO Dataset Constructor

This project reconstructs and generates the templates used for the SOBACO dataset proposed by the paper "Bias Mitigation or Cultural Commonsense? Evaluating LLMs with a Japanese Dataset".

## Overview

SOBACO (Social Bias and Cultural Commonsense) is a dataset designed to evaluate how well Large Language Models distinguish between stereotypical biases and legitimate cultural commonsense reasoning. This repository provides the template construction system to generate the dataset in both Japanese and Korean.

## Dataset Description

According to Appendix C of the paper, each template populates the dataset by 36, 72, or 108 samples, depending on the number of parameters (context types) in the expressions:

- **36 samples**: Templates without parameters (base templates)
- **72 samples**: Templates with 2 parameter variations
- **108 samples**: Templates with 3 parameter variations

## Repository Structure

```
.
├── main.py              # Dataset construction script
├── templates.py         # 66 Japanese language templates
├── ko_template.py       # 66 Korean language templates
├── pyproject.toml       # Project dependencies
└── README.md            # This file
```

## Files Description

### `templates.py`
Contains 66 Japanese templates (template1 through template66) with the following structure:
- `context`: Base context with placeholders `{name1}`, `{name2}`, and `{param}`
- `question`: The question to be answered
- `category`: Category of the question (e.g., 'hierarchical_relationship')
- `sample_idx`: Template index (1-66)
- `param`: List of parameter variations (empty list if no parameters)
- `additional_context_bias`: Additional context that introduces stereotypical bias
- `additional_context_culture`: Additional context with legitimate cultural information
- `biased_option_template`: Expected biased answer template
- `answer_template`: Correct answer template

### `ko_template.py`
Contains the same 66 templates translated into Korean, maintaining the same structure and logic.

### `main.py`
Dataset construction script featuring:
- Generator-based approach for memory efficiency
- Clean separation of concerns with `_generate_rows()` and `construct()` functions
- Support for both Japanese and Korean templates
- Constants for names and "I don't know" options
- Can be run standalone to generate `dataset.csv` and `ko_dataset.csv`

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

### Generate Datasets

Run the clean construction script to generate both Japanese and Korean datasets:

```bash
python clean.py
```

This will create:
- `dataset.csv`: Japanese dataset
- `ko_dataset.csv`: Korean dataset

### Use as a Module

```python
from clean import construct, NAMES, KO_NAMES
from templates import templates
from ko_template import ko_templates

# Generate data for a single Japanese template
data = construct(templates[0], NAMES)

# Generate data for a single Korean template  
ko_data = construct(ko_templates[0], KO_NAMES)
```

### Export Templates to JSON

```bash
# Export Japanese templates
python templates.py

# Export Korean templates
python ko_template.py
```

## Requirements

- Python >= 3.12
- pandas >= 2.3.3

Install dependencies:
```bash
pip install pandas
```

Or using the project configuration:
```bash
pip install -e .
```

## Key Features

- **Dual Language Support**: Both Japanese and Korean templates
- **Bias vs Culture Distinction**: Each template generates both biased and culturally informed contexts
- **Systematic Coverage**: Exhaustive permutations ensure comprehensive evaluation
- **Reproducibility**: Fixed random seed (42) for consistent "I don't know" option selection
- **Memory Efficient**: Generator-based implementation in `clean.py`

## Translation Notes

Several Japanese culture-specific templates had to be rewritten in order to make the dataset effective for Korean culture.

In the original dataset, "3歳と7歳の時に七五三のお祝いをした。" was used.
Since in Korea, there is no comparable event to 七五三, all-women's highschool and all-men's highschool was used.

Simillarly, "ひな祭り" was used for women-specific event for the Japanese templates. Since there is no comparable event in modern Korean culture, we had to change it to "명절 음식 준비" (lit. preparation of holiday dishes) for an event only experienced by women.

Sentences including "振袖" was changed to use "노리개" (decorative charm traditionally worn by women in Korea) instead, since there is no specific word for Korean traditional clothes that only women wears. Some cultural subtleties are lost, since "振袖" is usually only worn by unwed women (according to a Japanese-Korean Dictionary) and "노리개" is worn by both wed and unwed women in Korea. Just using "여성용 한복" (lit. Women's Hanbok) was considered, but including the word "women" in the query would most likely render the question meaningless so "노리개" was chosen instead.

DV was used in some of the templates, which was translated to "데이트폭력."
Since DV includes domestic violence between married couples, it does not translate 100%, but it was the closest word that is in common use in the Korean language.

"鯉のぼり" was used as an event for male children. Since there is no gender-specific events during childhood in Korea, mandatory military service was used to create the cultural context for the Korean template.

Unlike Japan, Korean people do not change their family name upon marriage, so all templates including the cultural context of changing their family name had to be changed. Until recently, it was culturally expected of the bride to prepare the furniture and home appliances, and the groom to prepare the residence. Therefore all template regarding name-changing was changed to "혼수마련" to test the cultural background of the bride preparing the furniture.

## Paper Reference

For more information about the SOBACO dataset and its evaluation methodology, please refer to the original paper:
"Bias Mitigation or Cultural Commonsense? Evaluating LLMs with a Japanese Dataset"