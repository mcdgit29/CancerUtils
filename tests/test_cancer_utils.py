import logging
import numpy as np
from CancerUtils.setup_logger import logger

logger.setLevel("DEBUG")


def test_icd9cm():

    logger.setLevel("DEBUG")
    logger.info('testing icd9 module .... ')
    from CancerUtils.icd9cm import breast_cancer_icd9, _all_cancer_icd9, cancer_icd9, crc_cancer_icd9, lung_cancer_icd9

    assert len(list(_all_cancer_icd9)) > 10

    inputs = list(_all_cancer_icd9)
    cnt = np.sum(list(map(cancer_icd9, inputs)))
    logger.debug(F" cancer_icd9 found: {cnt} of : {len(inputs)} ")
    assert cnt == len(inputs)

    inputs = [ 174.0,174.1,174.9]
    cnt =  np.sum(list(map(breast_cancer_icd9, inputs)))
    logger.debug(F"breast_cancer_icd9,found: {cnt} of : {len(inputs)} ")
    assert cnt == len(inputs)

    inputs = [162,162.0, 162.9]
    cnt =  np.sum(list(map(lung_cancer_icd9, inputs)))
    logger.debug(F"lung_cancer_icd9,found: {cnt} of : {len(inputs)} ")
    assert cnt == len(inputs)

    inputs = [153, 153.0, 153.9]
    cnt =  np.sum(list(map(crc_cancer_icd9, inputs)))
    logger.debug(F"crc_cancer_icd9,found: {cnt} of : {len(inputs)} ")
    assert cnt == len(inputs)
    logger.info('testing Cancer Utils package completed')


def test_icd9cm_code_str_matcing():
    logger.setLevel('DEBUG')
    from CancerUtils.icd9cm_code_str_matching import _icd9cm_dict, get_condition_tags
    s = "3051 7197 Z59 V620 495.9  331.0  301.11 301.22  291.0 \
     295.00 296.90  174.9  288.02  780.93 250.13 402.90 "
    for k, v in _icd9cm_dict.items():
        if v(s):
            logger.debug(F'{k} {v} ')

        else:

            logger.error(F'{k} {v} failed to detect icd9cm')
            raise ValueError

    assert get_condition_tags("3051") == ['smoking_or_nicotine_dependence']

    logger.info('icd9cm dict test completed ')


def test_icd10cm():
    logger.info('testing icd10 module ...')
    from CancerUtils.icd10cm import _all_cancer_icd10,_tobacco_user_icd10, _congnitive_impairment_icd10, \
    congative_impairment_icd10, _housing_instalbility_icd10, housing_instalbility_icd10, _low_income_icd10, \
        low_income_icd10, _social_indicator_icd10, _social_determinant_icd10, social_determinant_icd10,\
        social_indicator_icd10, family_cancer_history_icd10, personal_cancer_history_icd10, lung_cancer_icd10,\
        crc_cancer_icd10, tobacco_user_icd10


    assert len(list(_all_cancer_icd10)) > 10
    assert len(list(_tobacco_user_icd10)) > 10

    inputs = list(_congnitive_impairment_icd10)
    cnt =  np.sum(list(map(congative_impairment_icd10, inputs)))
    logger.debug(F" congative_impairment_icd10, found: {cnt} of : {len(inputs)} ")
    assert cnt == len(inputs)

    inputs = list(_housing_instalbility_icd10)
    cnt =  np.sum(list(map(housing_instalbility_icd10, inputs)))
    logger.debug(F" housing_instalbility_icd10, found: {cnt} of : {len(inputs)} ")
    assert cnt == len(inputs)

    inputs = list(_low_income_icd10)
    cnt =  np.sum(list(map(low_income_icd10, inputs)))
    logger.debug(F" low_income_icd10, found: {cnt} of : {len(inputs)} ")
    assert cnt == len(inputs)

    inputs = list(_social_determinant_icd10)
    cnt =  np.sum(list(map(social_determinant_icd10, inputs)))
    logger.debug(F" social_determinant_icd10, found: {cnt} of : {len(inputs)} ")
    assert cnt == len(inputs)

    inputs = list(_social_indicator_icd10)
    cnt =  np.sum(list(map(social_indicator_icd10, inputs)))
    logger.debug(F" social_indicator_icd10, found: {cnt} of : {len(inputs)} ")
    assert cnt == len(inputs)

    inputs = [ 'Z80','Z80.8', 'Z80.9']
    cnt =  np.sum(list(map(family_cancer_history_icd10, inputs)))
    logger.debug(F"family_cancer_history_icd10,found: {cnt} of : {len(inputs)} ")
    assert cnt == len(inputs)

    inputs = [ 'Z85','Z85.00', 'Z85.820', 'Z85.9']
    cnt =  np.sum(list(map(personal_cancer_history_icd10, inputs)))
    logger.debug(F"personal_cancer_history_icd10,found: {cnt} of : {len(inputs)} ")
    assert cnt == len(inputs)


    inputs = [ 'C34.01', 'C34', 'C34.00']
    cnt =  np.sum(list(map(lung_cancer_icd10, inputs)))
    logger.debug(F"lung_cancer_icd10,found: {cnt} of : {len(inputs)} ")
    assert cnt == len(inputs)

    inputs = [ 'C18', 'C18.0', 'C19', 'C20', 'C18.9']
    cnt =  np.sum(list(map(crc_cancer_icd10, inputs)))
    logger.debug(F"crc_cancer_icd10,found: {cnt} of : {len(inputs)} ")
    assert cnt == len(inputs)

    inputs =_tobacco_user_icd10
    cnt =  np.sum(list(map(tobacco_user_icd10, inputs)))
    logger.debug(F"tobacco_user_icd10,found: {cnt} of : {len(inputs)} ")
    assert cnt == len(inputs)
    logger.info('testing icd10 test completed')


def test_icd10matchin_str():
    logger.info('testing icd10 matching string module ...')
    from CancerUtils.icd10cm_code_str_matching import _icd10cm_dict, get_condition_tags
    s = "Z59.48  Z56.0 R26.2 F17.200 I11.0 R41.843 J44.1 \
    E10.1 E1123 D70.0 D14.0 C50.12 G30.1 F32.A  F60.8 F20.8 Y92.214"
    for k, v in _icd10cm_dict.items():
        if v(s):
            logger.debug(F'{k} {v} ')
        else:
            logger.error(F'{k} {v} failed to detect icd10cm')
            raise ValueError
    assert get_condition_tags('Z59.45') == ['housing_and_economics']
    logger.info('icd10cm dict test completed ')


def test_text():
    from CancerUtils.text import is_tobacco_user, increased_risk_for_breast_cancer,personal_breast_cancer,\
        family_history_of_cancer,family_history_of_breast_cancer, personal_cancer_history, personal_lung_cancer,\
        personal_crc_cancer, is_first_degree_relative, detect_any_negation, get_condtion_tags, get_insurance_tags,\
        get_cancer_history_tags
    logger.info('testing text module ... ')
    assert is_tobacco_user('Smoker')
    assert is_tobacco_user( 'Tobacco use')
    assert is_tobacco_user('does not use or abuse Tobacco') == False
    assert is_tobacco_user(  'Cigarette nicotine dependence without complication')
    assert is_tobacco_user( 'is not a smoker')==False


    logger.debug('testing increased_risk_for_breast_cancer_txt ...  ')
    assert increased_risk_for_breast_cancer('Increased risk of breast cancer')
    assert increased_risk_for_breast_cancer('Breast cancer screening, high risk patient')
    assert increased_risk_for_breast_cancer('Breast cancer genetic susceptibility')

    logger.debug('testing breast_cancer_txt ...  ')
    assert personal_breast_cancer('Breast neoplasm, Tis (LCIS)')
    assert personal_breast_cancer('History of breast cancer')
    assert personal_breast_cancer('Malignant neoplasm of breast')
    assert personal_breast_cancer('Breast cancer, stage 0')
    assert personal_breast_cancer('Malignant neoplasm of left breast in female, estrogen receptor negative')
    assert personal_breast_cancer('Breast cancer, stage 3')
    assert personal_breast_cancer('Malignant neoplasm of breast with BRCA1 gene mutation')
    assert personal_breast_cancer('Malignant neoplasm of breast (female), unspecified site')
    assert personal_breast_cancer('Malignant neoplasm of central portion of right breast in female, estrogen receptor positive')
    assert personal_breast_cancer('family history of breast cancer') == False
    assert personal_breast_cancer('Increased risk of breast cancer') == False
    assert personal_breast_cancer('Encounter for breast cancer screening') == False
    assert personal_breast_cancer('History of skin cancer') == False
    assert family_history_of_breast_cancer('family history of breast cancer')
    assert family_history_of_breast_cancer('history of breast cancer in mother')
    assert family_history_of_breast_cancer('history of breast cancer in mother')
    assert family_history_of_breast_cancer('colon cancer history') == False
    assert family_history_of_cancer('no history of breast cancer') == False
    assert personal_cancer_history( 'Breast cancer of upper-inner quadrant of left female breast')

    assert personal_cancer_history('History of thyroid cancer')
    assert personal_cancer_history( 'Breast cancer of upper-inner quadrant of left female breast')

    assert personal_cancer_history('Family history of prostate cancer in father')==False
    assert personal_cancer_history('Screen for colon cancer')==False

    assert family_history_of_cancer('History of thyroid cancer') == False
    assert family_history_of_cancer('prostate cancer in father')
    assert family_history_of_cancer('Family history of cancer')
    assert family_history_of_cancer('Colon cancer') ==False
    assert family_history_of_cancer( 'Breast cancer of upper-inner quadrant of left female breast')==False

    assert personal_crc_cancer('Carcinoma of colon')
    assert personal_crc_cancer( 'Colon cancer')
    assert personal_crc_cancer('Malignant tumor of colon')
    assert personal_crc_cancer('FBOT colon cancer test negative') == False

    assert is_first_degree_relative('Son')
    assert is_first_degree_relative( "mother")
    assert is_first_degree_relative('daughter')
    assert is_first_degree_relative('daughter in law') == False
    assert is_first_degree_relative('step son') ==False


    assert detect_any_negation('this is not what I meant')
    assert is_first_degree_relative('my dad thinks this is true')
    assert is_tobacco_user('that hypocryt smokes 2 packs a day')
    get_condtion_tags('chronic kidney disease due to alcoholism')
    assert len(get_insurance_tags('CIGNA, MEDICARE, "MEDICAID, BCBS, HMO, PPO workers comp, managage, care,tri-care')) == 9
    assert len(get_insurance_tags('')) == 0
    assert len(get_cancer_history_tags('family history of breast cancer in mother')) > 0

    assert len(get_cancer_history_tags('cancer neg_hx')) == 1
    assert len(get_cancer_history_tags('breast cancer survivor')) > 0
    logger.info('text module test complete')


def test_icd_from_raw_text():
    logger.info('testing icd from raw text ...')
    from CancerUtils.icd_from_raw_text import TextToIcd9
    nn = TextToIcd9().fit(10)

    text = 'family history of cancer'

    assert nn.transform('family history of breast cancer')['code'] == 'V163'
    assert nn.transform('breast cancer')['code'] == '2330'
    assert nn.transform( 'colon cancer')['code'] == '2303'
    assert nn.get_nearest_icd9('family history of depression') == 'V170'
    vec = nn.get_document_vector(text)

    logger.info('icd from raw text module test completed')



def test_ner():
    logger.info('testing ner module ....')
    from CancerUtils.ner import ProblemExtraction
    ner = ProblemExtraction()
    assert ner.get_problems('Encounter for screening for lung cancer. \family history of colon cancer. H/o Chronic kidney disease,  stage 3 (moderate)') == "colon cancer | chronic kidney disease  stage 3"
    logger.info('ner module testing completed')


if __name__ == "__main__":
    test_icd9cm()
    test_icd9cm_code_str_matcing()
    test_icd10cm()
    test_icd10matchin_str()
    test_text()
    test_icd_from_raw_text()
    logger.info('CancerUtils Test Completed')