import re
import os
import numpy as np
import logging
from CancerUtils.setup_logger import logger
from CancerUtils.utils import coerce_to_string

'''
Functions for extracting concepts from text Data

'''

class NLP:
    def __init__(self):
        self.nlp = None

    def load_nlp(self,  spacy_module = 'en_core_web_sm'):
        import spacy
        if self.nlp is None:

            try:
                self.nlp  = spacy.load(spacy_module )
                logger.info(F'spacy {spacy_module } loaded')
            except:
                logger.warn(F'spacy {spacy_module } failed to load, attempting to download...')
                os.system(F"python3 -m spacy download {spacy_module}")
                self.nlp = spacy.load(spacy_module)
                logger.info(F'spacy {spacy_module } loaded')
        else:
            logger.debug('nlp already loaded')

    def detect_any_negation(self, s):
        try:
            doc = self.nlp(s)
        except:
            self.load_nlp()
            doc = self.nlp(s)
        negation_tokens = [tok for tok in doc if tok.dep_ == 'neg']
        negation_head_tokens = [token.head for token in negation_tokens]
        if negation_head_tokens:
            return True
        else:
            return False

    def nlp(self, s):
        doc = self.nlp(s)
        return doc



def _pre_processor(s):
    results = str(s)\
        .lower()\
        .replace('  ', ' ')\
        .strip()
    return  ' ' + results


def is_at_risk(s):
    s = _pre_processor(s)
    keywords = ['at risk', 'risk of', 'risk for', 'high risk', 'elevated risk', 'suscepti']
    for word in keywords:
        if s.__contains__(word):
            return True
        else:
            pass
    else:
        return False


def detect_any_negation(s):
    s = _pre_processor(s)\
        .replace('receptor neg' , ' ')\
        .replace('without complication', ' ')

    keywords = ['negative', 'hx neg', 'hx_neg', 'no history', 'no family history', 'no fh', 'no f/m', 'no ho ', 'no h/o', 'does not', 'is not', "doesn't",
                "isn't", "no known", "is unknown"]
    results = any([s.lower().__contains__(word) for word in keywords])
    return results


def is_inlaw(s):
    s = _pre_processor(s)
    keywords = ['inlaw', 'step', 'by marriage', 'in law']
    for word in keywords:
        if s.__contains__(word):
            return True
        else:
            pass
    else:
        return False




def is_neg_or_benign_cancer_dx(s):
    s = _pre_processor(s)
    keywords = ['neg','benign','adenomas', 'fibromas', 'nonmela']
    for word in keywords:
        if all((s.__contains__(word),s.__contains__('receptor neg')==False)):
            return True
        else:
            pass
    else:
        return False


def  is_metastatic(s):
    s = _pre_processor(s)
    if detect_any_negation(s):
        return False
    else:
        return s.__contains__("metastas")


def is_tobacco_user(s):
    s = _pre_processor(s)
    tests  = [detect_any_negation(s) == False]
    keywords = ['smoker', 'tobacco', 'nicotine', 'smokes', 'smoking',
                'cigarette', 'pack a day', 'packs a day']

    if all(tests):
        for word in keywords:
            if s.__contains__(word):
                return True
            else:
                pass

    return False


def is_cancer(s):
    s = _pre_processor(s)
    if detect_any_negation(s):
        return False
    if is_neg_or_benign_cancer_dx(s):
        return False
    else:
        keywords = ['cancer', 'neoplas','malignant','carcinoma','metasta', 'tumor', 'lymphoma','sarcoma']
        return any([s.lower().__contains__(word) for word in keywords])



def is_first_degree_relative(s):
    s = _pre_processor(s)
    keywords =('mother', 'father', 'sister', 'brother', 'daughter', 'son', 'child', 'parent', 'mom ', 'dad ')
    tests = any([s.lower().__contains__(word) for word in keywords])
    return all((tests, is_inlaw(s) == False))



def is_family_reference(s):
    s = _pre_processor(s)
    keywords = ['grandfather', 'grandmother', 'uncle', 'aunt', 'relative', 'f/h', 'fh ', 'relative', 'family', 'cousin',
    'mother', 'father', 'sister', 'brother', 'daughter', 'son', 'child', 'parent', 'mom', 'dad', 'fm:']
    tests = any([s.lower().__contains__(word) for word in keywords])
    return all((tests,is_inlaw(s) == False ))


def replace_history(s):
    s = str(s).lower()\
    .replace('hx ' , ' history of ')\
    .replace('h/x ' , ' history of ')\
    .replace('f/m', ' family history of ')\
    .replace('f/h', ' family history of ')\
    .replace('fh: ',  ' family history of ')\
    .replace('fh ', ' family history of ')\
    .replace('fm ', ' family history of ')\
    .replace('fm: ', ' family history of ')\
    .replace('h/o', '  history of ')\
    .replace('h/0', '  history of ')\
    .replace('h/ ' , ' history of ')\
    .replace('hist ' , ' history ')
    return s


def strip_history(s):
    s = str(s).lower().replace(':', ' ')
    keywords = ['family history of', "personal history of", 'history of', 'h/x', 'h/o', 'ho ', 'hx', 'f/m', 'fh ','hist ', 'h/ ', 'h/0', 'of', '  ']
    for word in keywords:
        s = s.replace(word, ' ')
    return s.strip()


def is_history(s):
    s = replace_history(s)
    keywords = ('history')
    return any([s.lower().__contains__(word) for word in keywords])


def is_screening(s):
    s = _pre_processor(s)
    keywords = ('screen', 'test')
    return any([s.lower().__contains__(word) for word in keywords])


def is_encounter(s):
    s = _pre_processor(s)
    keywords = ('visit', 'encounter', 'office')
    return any([s.lower().__contains__(word) for word in keywords])

def advanced_directive(s):
    s = _pre_processor(s)
    keywords = ( 'advance', 'directive')
    return all([s.lower().__contains__(word) for word in keywords])

def is_confirming(s):
    s = _pre_processor(s)
    keywords = ('positve', 'confirm', 'valid')
    results = any([s.lower().__contains__(word) for word in keywords])
    if results == False:
        return False
    else:
        return all((results, detect_any_negation(s)==False))


def is_pregancy_related(s):
    s = _pre_processor(s)
    keywords = ('birth', 'is_pregancy_related', 'pregnancy', 'contraceptive', 'postpartum', 'natal', 'procreative', 'newborn')
    return any([s.lower().__contains__(word) for word in keywords])

def is_pediactric_related(s):
    s = _pre_processor(s)
    keywords = ('born','child','toddler', 'infant',  'childhood', 'pediactric', 'teenage', 'natal', 'newborn', 'kindergarden','kid ', 'adolesce')
    return any([s.lower().__contains__(word) for word in keywords])


def increased_risk_for_breast_cancer(s):
    s = _pre_processor(s)
    tests = [is_cancer(s),
    is_family_reference(s)==False,
    is_at_risk(s) == True,
    re.search('breast', s)]

    return all(tests)


def family_history_of_cancer(s):
    s = _pre_processor(s)
    tests = [is_cancer(s),
    is_family_reference(s),
    is_screening(s) == False]
    return all(tests)


def personal_cancer_history(s):
    s = _pre_processor(s)
    tests =[is_cancer(s),
    is_family_reference(s)==False,
    is_screening(s) == False,
    is_encounter(s) == False,
    is_at_risk(s) == False]
    return all(tests)


def personal_breast_cancer(s):
    s = _pre_processor(s)
    tests = [is_cancer(s),
    is_family_reference(s)==False,
    is_screening(s) == False,
    is_encounter(s) == False,
    is_at_risk(s) == False,
    re.search('breast', s)]
    return all(tests)


def personal_lung_cancer(s):
    s = _pre_processor(s)
    tests = [is_cancer(s),
    is_family_reference(s)==False,
    is_at_risk(s) == False,
    is_screening(s) == False,
    re.search('lung', s)]
    return all(tests)


def personal_crc_cancer(s):
    s = _pre_processor(s)
    tests = [is_cancer(s),
    is_family_reference(s)==False,
    is_screening(s) == False,
    is_at_risk(s) == False]
    keywords = ['crc', 'colon', 'colorectal', 'rectal']

    if all(tests):
        for word in keywords:
            if s.__contains__(word):
                return True
            else:
                pass

    return False


def family_history_of_breast_cancer(s):
    s = _pre_processor(s)
    tests = [re.search('breast', s),
    is_family_reference(s)==True,
    is_screening(s) == False,
    is_cancer(s)]
    return all(tests)


@coerce_to_string
def medicare(s):
    s = _pre_processor(s)
    keyword = 'medicare'
    return s.lower().__contains__(keyword)

@coerce_to_string
def medicaid(s):
    s = _pre_processor(s)
    keyword = 'medicaid'
    return s.lower().__contains__(keyword)

@coerce_to_string
def hmo(s):
    s = _pre_processor(s)
    keyword = 'hmo'
    return s.lower().__contains__(keyword)

@coerce_to_string
def ppo(s):
    s = _pre_processor(s)
    keyword = 'ppo'
    return s.lower().__contains__(keyword)

@coerce_to_string
def out_of_state(s):
    s = _pre_processor(s)
    keywords = ('out', 'state')
    return all([s.lower().__contains__(word) for word in keywords])

@coerce_to_string
def blue_cross(s):
    s = _pre_processor(s)
    keywords = ('bcbs', 'blue cross', 'blue shield', 'blue choice')
    return any([s.lower().__contains__(word) for word in keywords])

@coerce_to_string
def work_comp(s):
    s = _pre_processor(s)
    keywords = ('work', 'comp')
    return all([s.lower().__contains__(word) for word in keywords])

@coerce_to_string
def tri_care(s):
    s = _pre_processor(s)
    keywords = ('tri', 'care')
    return all([s.lower().__contains__(word) for word in keywords])

@coerce_to_string
def uhc(s):
    s = _pre_processor(s)
    keywords = ('uhc', 'united health')
    return any([s.lower().__contains__(word) for word in keywords])

@coerce_to_string
def managed_care(s):
    s = _pre_processor(s)
    keywords = ('manag', 'care')
    return all([s.lower().__contains__(word) for word in keywords])


@coerce_to_string
def aetna(s):
    s = _pre_processor(s)
    keyword= 'aetna'
    return s.lower().__contains__(keyword)

@coerce_to_string
def medicare_advantage(s):
    s = _pre_processor(s)
    keywords = ('medicare', 'advantage')
    return all([s.lower().__contains__(word) for word in keywords])

@coerce_to_string
def comercial(s):
    s = _pre_processor(s)
    keyword = 'comercial'
    return s.lower().__contains__(keyword)

@coerce_to_string
def cigna(s):
    s = _pre_processor(s)
    keyword = 'cigna'
    return s.lower().__contains__(keyword)


@coerce_to_string
def select_health(s):
    s = _pre_processor(s)
    keywords = ('select', 'health')
    return all([s.lower().__contains__(word) for word in keywords])


insurance_tag_dict = {
"select_health":select_health,
"cigna":cigna,
"comercial":  comercial,
"medicare_advantage":  medicare_advantage,
"aetna": aetna,
"managed_care":  managed_care,
"uhc":  uhc,
"tri_care": tri_care,
"work_comp": work_comp,
"blue_cross": blue_cross,
"out_of_state":out_of_state,
"ppo": ppo,
"hmo": hmo,
"medicaid": medicaid,
"medicare": medicare
}


cancer_history_dict = {
'is_cancer': is_cancer,
'family_history_of_cancer' :  family_history_of_cancer,
'family_history_of_breast_cancer':  family_history_of_breast_cancer,
'first_degree_relative': is_first_degree_relative,
'tobacco_user':  is_tobacco_user,
'crc_cancer' : personal_crc_cancer,
'lung_cancer':  personal_lung_cancer,
'increased_risk_for_breast_cancer': increased_risk_for_breast_cancer,
'breast_cancer': personal_breast_cancer,
'personal_cancer_history': personal_cancer_history,
'negation': detect_any_negation,
'metastatic': is_metastatic,
'confirmed_neg_for_cancer': is_neg_or_benign_cancer_dx
 }


condition_tag_dict = {'family_history_of_cancer' :  family_history_of_cancer,
'family_history_of_breast_cancer':  family_history_of_breast_cancer,
'first_degree_relative': is_first_degree_relative,
'tobacco_user':  is_tobacco_user,
'crc_cancer' : personal_crc_cancer,
'lung_cancer':  personal_lung_cancer,
'increased_risk_for_breast_cancer': increased_risk_for_breast_cancer,
'breast_cancer': personal_breast_cancer,
'personal_cancer_history': personal_cancer_history,
'negation': detect_any_negation,
'pregancy_related': is_pregancy_related,
'confirming': is_confirming,
'encounter': is_encounter,
'screening': is_screening,
'history':  is_history,
'family_reference' :is_family_reference,
'is_inlaw':is_inlaw,
'metastatic': is_metastatic,
'advanced_directive': advanced_directive,
'is_pediactric_related': is_pediactric_related
}


condition_tag_dict.update(cancer_history_dict)

@coerce_to_string
def get_condtion_tags(s):
    d = []
    for key, func in condition_tag_dict.items():
        if func(s):
            d.append(key)
    return np.unique(d)

@coerce_to_string
def get_cancer_history_tags(s):
    d = []
    for key, func in cancer_history_dict.items():
        if func(s):
            d.append(key)
    return np.unique(d)



@coerce_to_string
def get_insurance_tags(s):
    d = []
    for key, func in insurance_tag_dict.items():
        if func(s):
            d.append(key)
    return np.unique(d)

