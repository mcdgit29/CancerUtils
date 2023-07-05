import json
import logging
import numpy as np
import pandas as pd
import re
from CancerUtils.setup_logger import logger
from CancerUtils.utils import apply_with_tokenizer, coerce_to_string


def housing_and_economics(s):
    s = str(s).upper()
    return s.__contains__('Z59')

def employment_and_unemployment(s):
    s = str(s).upper()
    return s.__contains__('Z56')

def abnormalities_gait_and_mobility(s):
    s = str(s).upper()
    return s.__contains__('R26')

def smoking_or_nicotine_dependence(s):
    s = str(s).upper().replace('.', '')
    tests = (s.__contains__('Z720'),
    s.__contains__('F17'),
    s.__contains__('F17')
     )
    return any(tests)

def hypertensive_heart_disease(s):
    s = str(s).upper()
    return s.__contains__('I11')

def chronic_obstructive_pulmonary_disease(s):
    s = str(s).upper()
    return s.__contains__('J44')

def cognitive_functions_and_awareness(s):
    s = str(s).upper()
    return s.__contains__('R41')

def diabetes_mellitus_t1_or_12(s):
    s = str(s).upper().replace('.', '')
    tests = (s.__contains__('E10'),
    s.__contains__('E11'),
     )
    return any(tests)

def neutropenia(s):
    s = str(s).upper()
    return s.__contains__('D70')

def any_cancer(s):
    s = str(s).upper().replace('.', '')
    keys = ['C'] + [F'D{i}' if len(str(i))==2 else F'D0{i}' for i in range(0,50)  ]
    return any(pd.Series(keys).apply(lambda x: s.__contains__(x)))

def breast_cancer(s):
    s = str(s).upper().replace('.', '')
    return s.__contains__('C50')


def external_morbidity(s):
    s = str(s).upper().replace('.', '')
    if re.search('[V-Y][0-9]{2}', s):
        return True
    else:
        return False

def alzheimer(s):
    s = str(s).upper().replace('.', '')
    return s.__contains__('G30')

def non_mood_psychotic_disorders(s):
    s = str(s).upper().replace('.', '')
    if re.search('F2[0-9]{1}', s):
        return True
    else:
        return False

def mood_affective_disorders(s):
    s = str(s).upper().replace('.', '')
    if re.search('F3[0-9]{1}', s):
        return True
    else:
        return False

def personality_disorders(s):
    s = str(s).upper().replace('.', '')
    return s.__contains__('F60')

def heart_failure(s):
    s = str(s).upper().replace('.', '')
    test = (s.__contains__("I110"),
        s.__contains__("I130"),
        s.__contains__("I132"),
        s.__contains__("I50"))
    return any(test)


_icd10cm_dict = {
    'external_morbidity':  external_morbidity,
    'mood_affective_disorders':mood_affective_disorders,
    'non_mood_psychotic_disorders': non_mood_psychotic_disorders,
    'alzheimer':  alzheimer,
    'breast_cancer':breast_cancer,
    'any_cancer':any_cancer,
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
    for key, func in _icd10cm_dict.items():
        if func(s):
            d.append(key)
    return np.unique(d)


