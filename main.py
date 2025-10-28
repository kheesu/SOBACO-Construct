import itertools
import random
from collections import defaultdict
import pandas as pd


# --- Constants ---
# Define options as a constant outside the function
IDK_OPTIONS = ['わからない', '判断できない', '回答できない', '情報が不十分', 'どちらでもない']
NAMES = ['佐藤', '鈴木', '田中']

KO_IDK_OPTIONS = ['알 수 없다', '선택할 수 없다', '답 할 수 없다', '정보가 부족하다', '양쪽 다 아니다']
KO_NAMES = ['김', '이', '박']

def _generate_rows(template, names, idks):
    """
    A generator function that yields one data row (as a dict) for each
    permutation. This contains all the complex nested logic.
    """
    question = template['question']
    category = template['category']
    sample_idx = template['sample_idx']
    params_list = template.get('param') or [None]

    for param in params_list:
        for name1, name2 in itertools.permutations(names, 2):
            base_context = template['context'].replace('{name1}', name1).replace('{name2}', name2)
            
            for type in ['bias', 'culture']:
                context = base_context
                if param is not None:
                    context = context.replace('{param}', param)
                    
                context_key = 'additional_context_bias' if type == 'bias' else 'additional_context_culture'
                additional_context = template[context_key].replace('{name1}', name1).replace('{name2}', name2)

                idk = random.choice(idks)
                
                if type == 'bias':
                    answer = idk
                    biased_option = template['biased_option_template'].replace('{name1}', name1).replace('{name2}', name2)
                else:
                    if template['biased_option_template'] == 'IDK':
                        answer = idk
                    else:
                        answer = template['answer_template'].replace('{name1}', name1).replace('{name2}', name2)
                    biased_option = None
                    
                    
                for options in itertools.permutations([name1, name2, idk]):
                    yield {
                        'context': context,
                        'additional_context': additional_context,
                        'type': type,
                        'question': question,
                        'options': options,
                        'answer': answer,
                        'biased_option': biased_option,
                        'category': category,
                        'sample_idx': sample_idx,
                        'name1': name1,
                        'name2': name2,
                        'param': param
                    }

def construct(template, names, idks):
    """
    Constructs a dataset dictionary from a template and a list of names.
    """
    constructed = defaultdict(list)

    for data_row in _generate_rows(template, names, idks):
        for key, value in data_row.items():
            constructed[key].append(value)
            
    return dict(constructed)

if __name__ == '__main__':
    import json
    
    with open('ko_template.json', 'r') as fp:
        ko_templates = json.load(fp)
    all_rows = []
    for template in ko_templates:
        all_rows.extend(_generate_rows(template, KO_NAMES, KO_IDK_OPTIONS))
    df = pd.DataFrame(all_rows)
    df.to_csv('ko_dataset.csv', index=False)
    
    with open('template.json', 'r') as fp:
        templates = json.load(fp)
    all_rows = []
    for template in templates:
        all_rows.extend(_generate_rows(template, NAMES, IDK_OPTIONS))
    df = pd.DataFrame(all_rows)
    df.to_csv('dataset.csv', index=False)