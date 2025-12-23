"""Configuration settings for SOBACO constructor."""

from pathlib import Path
from typing import List

# Project root directory
ROOT_DIR = Path(__file__).parent.parent

# Data directories
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
GENERATED_DATA_DIR = DATA_DIR / "generated"

# Template directories
TEMPLATES_DIR = ROOT_DIR / "src" / "templates"

# Supported languages
LANGUAGES = ["ja", "ja-ko", "ja-zh", "ko", "ko-jp", "ko-zh", "zh", "zh-ko", "zh-ja", "ko-v2", "ko-jp-v2", "ko-zh-v2"]

# Name lists for each language
NAMES = {
    "ja": ['佐藤', '鈴木', '田中'],
    "ja-ko": ['사토', '스즈키', '다나카'],
    "ja-zh": ['佐藤', '铃木', '田中'],
    "ko": ['김', '이', '박'],
    "ko-jp": ["キム", "イ", "パク"],
    "ko-zh": ["金", "李", "朴"],
    "zh": ['小张', '小李', '小王'],
    "zh-ko": ['장씨', '리씨', '왕씨'],
    "zh-ja": ['張さん', '李さん', '王さん'],
    "ko-v2": ['김', '이', '박'],
    "ko-jp-v2": ['キム', 'イ', 'パク'],
    "ko-zh-v2": ['金', '李', '朴'],
}

# IDK (I don't know) options for each language
IDK_OPTIONS = {
    "ja": ['わからない', '判断できない', '回答できない', '情報が不十分', 'どちらでもない'],
    "ja-ko": ['알 수 없다', '선택할 수 없다', '답 할 수 없다', '정보가 부족하다', '양쪽 다 아니다'],
    "ja-zh": ['不知道', '无法判断', '无法回答', '信息不足', '都不是'],
    "ko": ['알 수 없다', '선택할 수 없다', '답 할 수 없다', '정보가 부족하다', '양쪽 다 아니다'],
    "ko-jp": ['わからない', '判断できない', '回答できない', '情報が不十分', 'どちらでもない'],
    "ko-zh": ['不知道', '无法判断', '无法回答', '信息不足', '都不是'],
    "zh": ['无法判断', '不清楚', '无法回答', '信息不足', '都不是'],
    "zh-ko": ['알 수 없다', '선택할 수 없다', '답 할 수 없다', '정보가 부족하다', '양쪽 다 아니다'],
    "zh-ja": ['わからない', '判断できない', '回答できない', '情報が不十分', 'どちらでもない'],
    "ko-v2": ['알 수 없다', '선택할 수 없다', '답 할 수 없다', '정보가 부족하다', '양쪽 다 아니다'],
    "ko-jp-v2": ['わからない', '判断できない', '回答できない', '情報が不十分', 'どちらでもない'],
    "ko-zh-v2": ['不知道', '无法判断', '无法回答', '信息不足', '都不是'],
}

# Categories
CATEGORIES = [
    "hierarchical_relationship",
    "gender", 
    "age"
]

def get_names(language: str) -> List[str]:
    """Get names for a specific language."""
    return NAMES.get(language, NAMES["ja"])

def get_idk_options(language: str) -> List[str]:
    """Get 'I don't know' options for a specific language."""
    return IDK_OPTIONS.get(language, IDK_OPTIONS["ja"])
