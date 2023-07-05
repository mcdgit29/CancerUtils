
import json
import logging
import numpy as np
import re
from CancerUtils.setup_logger import logger
import pickle
import pkg_resources

def _load_data(resource_name):
    return pickle.load(
        pkg_resources.resource_stream("CancerResearch", resource_name))

from CancerUtils.utils import load_resource

'''
Functions for extracting concepts from ICD10cm Data
### ICD10CM Module Usage

Available functions:

  + cancer_icd10
  + family_cancer_history_icd10
  + personal_cancer_history_icd10
  + breast_cancer_icd10
  + lung_cancer_icd10
  + crc_cancer_icd10
  + tobacco_user_icd10
  + congative_impairment_icd10
  + housing_instalbility_icd10
  + low_income_icd10
  + social_determinant_icd10
  + social_indicator_icd10
  + frailty_icd10
  + heart_failure_icd10

    Example Usage:
  ```python3
  from CancerUtils.icd10cm import cancer_icd10
  inputs = 'C20'
  cancer_icd10(inputs)
  ```
'''


_all_cancer_icd10 = set(load_resource('/resources/all_cancer_icd10.txt'))
_tobacco_user_icd10 = set(load_resource('/resources/tobacco_user_icd10.txt'))
_congnitive_impairment_icd10 = set(load_resource('/resources/cognitive_impairment_icd10.txt'))
_housing_instalbility_icd10 = set(load_resource('/resources/housing_instability_icd10.txt'))
_low_income_icd10 = set(load_resource('/resources/low_income_icd10.txt'))
_social_determinant_icd10 = set(load_resource('/resources/social_determinant_icd10.txt'))
_social_indicator_icd10 = set(load_resource('/resources/social_indicator_icd10.txt'))
_frailty_icd10 = set(load_resource('/resources/frailty_icd10.txt'))
_heart_failure_icd10= set(load_resource('/resources/heart_failure_icd10.txt'))

def cancer_icd10(s):
    '''
    param: s str icd10cm code, example "Z80.1"
    returns bool

    '''
    s = str(s).strip()
    if s in _all_cancer_icd10:
        return True
    else:
        return False

def family_cancer_history_icd10(s):
    '''
    param: s str icd10cm code, example "Z80.1"
    returns bool

    '''
    s = str(s).strip()
    s = re.sub('[.].+', '',s )
    if s == 'Z80':
        return True
    else:
        return False

def personal_cancer_history_icd10(s):
    '''
    param: s str icd10cm code, example "Z80.1"
    returns bool

    '''
    s = str(s).strip()
    s = re.sub('[.].+', '', s )
    if s == 'Z85':
        return True
    else:
        return False

def breast_cancer_icd10(s):
    '''
    param: s str icd10cm code, example "Z80.1"
    returns bool

    '''
    s = str(s).strip()
    s = re.sub('[.].+', '', s )
    if s == 'C50':
        return True
    else:
        return False

def lung_cancer_icd10(s):
    '''
    param: s str icd10cm code, example "Z80.1"
    returns bool

    '''
    s = str(s).strip()
    s = re.sub('[.].+', '', s )
    if s == 'C34':
        return True
    else:
        return False

def crc_cancer_icd10(s):
    '''
    param: s str icd10cm code, example "Z80.1"
    returns bool

    '''
    s = str(s).strip()
    s = re.sub('[.].+', '', s )
    if s == 'C18':
        return True
    elif s == 'C19':
        return True
    elif s == 'C20':
        return True
    else:
        return False

def tobacco_user_icd10(s):
    '''
    param: s str icd10cm code, example "Z80.1"
    returns bool

    '''
    s = str(s).strip()
    if s in _tobacco_user_icd10:
        return True
    else:
        return False

def congative_impairment_icd10(s):
    '''
    param: s str icd10cm code, example "Z80.1"
    returns bool

    '''
    s = str(s).strip()
    if s in _congnitive_impairment_icd10:
        return True
    else:
        return False

def housing_instalbility_icd10(s):
    '''
    param: s str icd10cm code, example "Z80.1"
    returns bool

    '''
    s = str(s).strip()
    if s in _housing_instalbility_icd10:
        return True
    else:
        return False


def low_income_icd10(s):
    '''
    param: s str icd10cm code, example "Z80.1"
    returns bool

    '''
    s = str(s).strip()
    if s in _low_income_icd10:
        return True
    else:
        return False

def social_determinant_icd10(s):
    '''
    param: s str icd10cm code, example "Z80.1"
    returns bool

    '''
    s = str(s).strip()
    if s in _social_determinant_icd10:
        return True
    else:
        return False

def social_indicator_icd10(s):
    '''
    param: s str icd10cm code, example "Z80.1"
    returns bool

    '''
    s = str(s).strip()
    if s in _social_indicator_icd10:
        return True
    else:
        return False


def frailty_icd10(s):
    '''
    param: s str icd10cm code, example "Z80.1"
    returns bool

    '''
    s = str(s).strip()
    if s in _frailty_icd10:
        return True
    else:
        return False


def heart_failure_icd10(s):
    '''
    param: s str icd10cm code, example "Z80.1"
    returns bool

    '''
    s = str(s).strip()
    if s in _heart_failure_icd10:
        return True
    else:
        return False

