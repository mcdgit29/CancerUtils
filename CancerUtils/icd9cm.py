
import json
import logging
import re
import numpy as np
from CancerUtils.setup_logger import logger
from CancerUtils.utils import load_resource

_all_cancer_icd9 = set(load_resource('resources/all_cancer_icd9.txt'))
_heart_failure_icd9 = set(load_resource('resources/heart_failure_icd9.txt'))

'''
Functions for extracting concepts from ICD9 Data

### ICD9CM Module

Available functions:
  + family_cancer_history_icd9
  + personal_malignant_neoplasm_history_icd9
  + malignant_neoplasm_icd9
  + cancer_icd9
  + breast_cancer_icd9
  + lung_cancer_icd9
  + crc_cancer_icd9
  + heart_failure_icd9

Example Usages 
    
    ```python3
    from CancerUtils.icd9cm import breast_cancer_icd9
    inputs = '174.0,174.1,174.9'
    breast_cancer_icd9(inputs)
    ```

'''

def family_cancer_history_icd9(s):
    '''
    param: s str icd9cm code, example "V16.1"
    returns bool

    '''
    s = str(s).strip()
    s = re.sub('[.].+', '',s )
    if s == 'V16':
        return True
    else:
        return False

def personal_malignant_neoplasm_history_icd9(s):
    '''
    param: s str icd9cm code, example "V16.1"
    returns bool

    '''
    s = str(s).strip()
    s = re.sub('[.].+', '',s )
    if s == 'V10':
        return True
    else:
        return False

def malignant_neoplasm_icd9(s):
    '''
    param: s str icd9cm code, example "V16.1"
    returns bool

    '''
    try:
        v = int(float(str(s).strip()))
        if all((v>=140, v<210)):
            return True
        else:
            return False
    except ValueError:
        return False

def cancer_icd9(s):
    '''
    param: s str icd9cm code, example "V16.1"
    returns bool

    '''
    s = str(s).strip()
    if s in _all_cancer_icd9:
        return True
    else:
        return False

def breast_cancer_icd9(s):
    '''
    param: s str icd9cm code, example "V16.1"
    returns bool

    '''
    s = str(s).strip()
    s = re.sub('[.].+', '',s )
    if s == '174':
        return True
    else:
        return False


def lung_cancer_icd9(s):
    s = str(s).strip()
    s = re.sub('[.].+', '',s )
    if s == '162':
        return True
    else:
        return False

def crc_cancer_icd9(s):
    '''
    param: s str icd9cm code, example "V16.1"
    returns bool

    '''
    s = str(s).strip()
    s = re.sub('[.].+', '',s )
    if s == '153':
        return True
    else:
        return False


def heart_failure_icd9(s):
    '''
    param: s str icd9cm code, example "V16.1"
    returns bool

    '''
    s = str(s).strip()
    if s in _heart_failure_icd9:
        return True
    else:
        return False
