import json
import logging
import numpy as np
import pandas as pd
import re
from CancerUtils.setup_logger import logger
import pickle
import pkg_resources
from CancerUtils.utils import apply_with_tokenizer, coerce_to_string


def housing_and_economics(s):
    s = str(s).upper()
    return s.__contains__('Z59')

def employment_and_unemployment(s):
    s = str(s).upper()
    return s.__contains__('V620')

@apply_with_tokenizer
def abnormalities_gait_and_mobility(s):
    s = str(s).upper()
    return s.startswith('7197')

@apply_with_tokenizer
def smoking_or_nicotine_dependence(s):
    s = str(s).upper().replace('.', '')
    tests = (s.__contains__('V1582'),
    s.startswith('3051'),
    s.startswith('64900'),
    s.startswith('64901'),
    s.startswith('64902'),
    s.startswith('64903'),
    s.startswith('64904'),
    s.startswith('98984')
     )
    return any(tests)

@apply_with_tokenizer
def hypertensive_heart_disease(s):
    s = str(s).upper()
    if all(((s.startswith('4'), re.search('4[0|2]{1}[0-9]{1}', s)))):
        return True
    else:
        return False

@apply_with_tokenizer
def chronic_obstructive_pulmonary_disease(s):
    s = str(s).upper()
    if all(((s.startswith('49'), re.search('49[0-9]{1}', s)))):
        return True
    else:
        return False

@apply_with_tokenizer
def cognitive_functions_and_awareness(s):
    s = str(s).upper().replace('.', '')
    keys = ['78097', '78093', '7818', '797' '79951', '79953', '79954', '79955' ,
    "79959", "R419"]
    return any(pd.Series(keys).apply(lambda x: s.startswith(x)))

@apply_with_tokenizer
def diabetes_mellitus_t1_or_12(s):
    s = str(s).upper().replace('.', '')
    return s.__contains__('250')

@apply_with_tokenizer
def neutropenia(s):
    s = str(s).upper().replace('.', '')
    return s.startswith('2880')

@apply_with_tokenizer
def breast_cancer(s):
    s = str(s).upper().replace('.', '')
    return s.startswith('174')

@apply_with_tokenizer
def mood_affective_disorders(s):
    keys = ['311', '296']
    return any(pd.Series(keys).apply(lambda x: s.startswith(x)))

@apply_with_tokenizer
def non_mood_psychotic_disorders(s):
    s = str(s).upper().replace('.', '')
    keys = ["295", "297", "298"]
    return any(pd.Series(keys).apply(lambda x: s.startswith(x)))

@apply_with_tokenizer
def alzheimer(s):
    s = str(s).upper().replace('.', '')
    return s.startswith('331')

@apply_with_tokenizer
def personality_disorders(s):
    s = str(s).upper().replace('.', '')
    return s.startswith('301')


_icd9cm_dict = {
    'mood_affective_disorders':mood_affective_disorders,
    'non_mood_psychotic_disorders': non_mood_psychotic_disorders,
    'alzheimer':  alzheimer,
    'breast_cancer':breast_cancer,
    'neutropenia': neutropenia,
    'diabetes_mellitus_t1_or_12':diabetes_mellitus_t1_or_12,
    'cognitive_functions_and_awareness': cognitive_functions_and_awareness,
    'chronic_obstructive_pulmonary_disease':chronic_obstructive_pulmonary_disease,
    'hypertensive_heart_disease': hypertensive_heart_disease,
    'smoking_or_nicotine_dependence': smoking_or_nicotine_dependence,
    'abnormalities_gait_and_mobility': abnormalities_gait_and_mobility,
    'employment_and_unemployment': employment_and_unemployment,
    'housing_and_economics':  housing_and_economics,
    'personality_disorders': personality_disorders
    }

@coerce_to_string
def get_condition_tags(s):
    d = []
    for key, func in _icd9cm_dict.items():
        if func(s):
            d.append(key)
    return np.unique(d)





