import os
import pandas as pd
import numpy as np
import re
import logging
from CancerUtils.setup_logger import logger
from datetime import datetime
from pyelixhauser.icd10cm_cmr_v2022 import comorbidity_from_array
from CancerUtils.icd10cm_code_str_matching import get_condition_tags as get_condtion_tags_icd10
from CancerUtils.icd9cm_code_str_matching import  get_condition_tags as get_condtion_tags_icd9
from CancerUtils.utils import key_error_return_none, value_error_return_none, key_error_return_array, key_error_return_dict
from CancerUtils.text import get_cancer_history_tags,insurance_tag_dict, condition_tag_dict, strip_history
from CancerUtils.text import cancer_history_dict as chd
from CancerUtils.text import get_condtion_tags as get_condtion_tags_text
from itertools import chain

n_days_prior = 10 * 365

raise NotImplementedError("This Module has not been Implemented in the public version of the code")
class ScreeningTests:
    def __init__(self, df):
        self.pid_col = 'DEID'
        self.proc_col = 'ORDER_PROC'
        self.status_col = 'ORDER_STATUS'
        self.order_dt = 'ORDER_DATE'
        self.proc_dt = 'PROC_START_DATE'
        self.df = df.sort_values(by=self.pid_col)
        self.df.loc[:, self.proc_col ] = self.df.loc[:, self.proc_col].str.lower()
        self.df.loc[:, self.status_col] = self.df.loc[:, self.status_col].str.lower()
        self.df.loc[:, self.order_dt] = pd.to_datetime(self.df.loc[:, self.order_dt])
        self.df.loc[:, self.proc_dt] = pd.to_datetime(self.df.loc[:, self.proc_dt] )
        self.df = self.df.set_index(self.pid_col)
        logger.debug(F'screening tests loaded with {self.df.shape[0]} rows')

    def  get_input_col_names(self):
        return [self.proc_col, self.status_col ,self.order_dt  ]

    @key_error_return_dict
    def query_dict(self, pid, dt=datetime.today()):
        x = self.df.loc[[pid], :].copy()
        x = x.loc[(x.loc[:, self.order_dt]<=dt) & (x.loc[:, self.proc_dt]<=dt), :]
        return x.loc[:, [self.order_dt ,self.proc_dt,  self.status_col, self.proc_col ]].to_dict('series')

    @key_error_return_none
    def first_ordered_dt(self, pid, test_type=None):
        x = self.df.loc[[pid], :].copy()
        if test_type:
            index =  x.loc[:, self.proc_col].fillna('').str.contains(test_type.lower())
            x = x.loc[index, :]
        else:
            pass
        date = x.loc[:, self.order_dt].min()
        if np.isnan(date.year):
            return None
        else:
            return date

    @value_error_return_none
    @key_error_return_none
    def first_completed_dt(self, pid, test_type=None):

        x = self.df.loc[[pid], :].copy()
        if test_type:
            x = x.loc[x.loc[:, self.proc_col].str.lower().str.contains(test_type.lower()), :]
        else:
            pass
        date = x.loc[x.loc[:, self.status_col].fillna('').str.contains('comp'), self.proc_dt]
        date = date.min()
        if np.isnan(date.year):
            return None
        else:
                return date
    @value_error_return_none
    @key_error_return_none
    def first_sent_dt(self, pid, test_type=None):
        x = self.df.loc[[pid ], :].copy()
        if test_type:
            x = x.loc[x.loc[:, self.proc_col].str.contains(test_type.lower()), :]
        else:
            pass
        date = x.loc[x.loc[:, self.status_col].fillna('').str.contains('sent'), self.order_dt]
        date = date.min()
        if np.isnan(date.year):
            return None
        else:
            return date

    @value_error_return_none
    @key_error_return_none
    def days_to_complete(self, pid, test_type=None):
        order_dt = self.first_ordered_dt(pid, test_type)
        comp_dt = self.first_completed_dt(pid, test_type)
        logger.debug(F' searching for test {test_type} , order dt {order_dt} comp_dt {comp_dt}')
        try:
            if order_dt.date() <= comp_dt.date():
                return int((comp_dt - order_dt)/ np.timedelta64(1, 'D'))
            else:
                raise AttributeError
        except AttributeError:
            return None

    @value_error_return_none
    @key_error_return_none
    def days_to_send(self, pid, test_type=None):
        order_dt = self.first_ordered_dt(pid, test_type)
        comp_dt = self.first_sent_dt(pid, test_type)
        logger.debug(F' days to sent searching for test {test_type} , order dt {order_dt} sent_dt {comp_dt}')
        try:
            if order_dt.date() <= comp_dt.date():
                return int((comp_dt - order_dt)/ np.timedelta64(1, 'D'))
            else:
                raise AttributeError
        except AttributeError:
            return None

    def case_control_detection(self, pid, test_type=None, n_days=180, mask_same_day=False, ref_dt=None):
        logger.debug(F'running case control detection on pid {pid} for test type {test_type}')
        results = dict()

        results['order_dt'] = self.first_ordered_dt(pid, test_type)
        results['comp_dt'] = self.first_completed_dt(pid, test_type)
        results['sent_dt'] =  self.first_sent_dt(pid, test_type)
        ref_dt = pd.to_datetime(ref_dt)
        results['n_comp_days'] = self.days_to_complete(pid, test_type)
        results['n_sent_days'] = self.days_to_send(pid, test_type)
        results['ref_dt'] = ref_dt
        results['pid'] = pid

        ## finds controls
        try:
            results['n_days_before_reference'] = int((results['ref_dt'] - results['order_dt'])/ np.timedelta64(1, 'D'))
        except TypeError:
            results['n_days_before_reference'] = None
        results['case_control'] = 'mask'
        try:
            if all((mask_same_day,results['n_comp_days']>0, results['n_comp_days']<=n_days)):
                results['case_control'] = 'control'
            elif all((mask_same_day==False, results['n_comp_days']>=0, results['n_comp_days']<=n_days)):
                results['case_control'] = 'control'
            else:
                raise TypeError
        except TypeError:
            logger.debug('control detection rules ended without detecting a control ')
            pass
        ## find cases
        try:
            logger.debug('evaluating case rules..')
            if all((results['order_dt']!=None,
            results['n_comp_days']== None,
            results['n_sent_days' ]==None )):
                results['case_control'] = 'case'
            else:
                if all((results['order_dt']!=None,
                results['n_comp_days'] > n_days,results['n_sent_days'] == None )):
                    results['case_control'] = 'case'
                else:
                    if all((results['order_dt']!=None,
                    results['n_comp_days'] >  n_days,
                    results['n_sent_days']> n_days )):
                        results['case_control'] = 'case'
                    else:
                        raise TypeError
        except TypeError:
            logger.debug('case detection rules ended with out detecting a case')
        return results


class Demographics:
    def __init__(self, df):
        self.pid_col = 'DEID'
        self.race_col = "RACE"
        self.gender_col = "GENDER"
        self.marital_stat_col = "MARITAL_STATUS"
        self.age_col = 'BIRTH_YEAR'
        self.fips_col = "FIPS"
        self.df = df.sort_values(by=self.pid_col)
        self.df = self.df.set_index(self.pid_col)
        self.generations = {'Gen Z': (1997, 2012),
                            'Millennials': (1981,  1996),
                            'Gen X':	(1965, 1980),
                            'Boomers':	(1946 ,1964),
                            'Silent Generation':(1928, 1945),
                            'Greatest Generation': (1900, 1927)}
        logger.debug(F'screening tests loaded with {self.df.shape[0]} rows')


    def query_dict(self, pid, dt=datetime.today()):
        x = self.df.loc[[pid], :].copy()
        return x.to_dict('series')

    def race_ohe(self, x):
        x = str(x).lower()
        array = pd.Series([0,0,0], index=['White-Cauc', "African-American","Asian"])
        if any(((x.__contains__('white'), x.__contains__('cauc')))):
            array.loc['White-Cauc'] = 1
        if any(((x.__contains__('black'),(x.__contains__('african am'))))):
            array.loc["African-American"] = 1
        if all((x.__contains__('asian'), array.sum()==0)):
            array.loc["Asian"] =1
        if array.sum() > 1:
            logger.info(F'multiple race detection from {x}')
        return array

    def gender_ohe(self, x):
        x = str(x).lower()
        array = pd.Series([0,0,0], index=['Female', 'Male', "Gender_Other"])
        if x.__contains__('fem'):
            array.loc['Female'] = 1
        if all(((x.__contains__('male'),array.sum()==0))):
            array.loc["Male"] = 1
        if array.sum() == 0:
            array.loc["Gender_Other"] = 1
        return array

    def marital_status_ohe(self, x):
        x = str(x).lower()
        array = pd.Series([0,0,0,0], index=['Married', 'Single', "Divorced_or_Sep", "Wpidowed"])
        if x.__contains__('mar'):
            array.loc['Married'] = 1
        if x.__contains__("sing"):
            array.loc["Single"] = 1
        if x.__contains__("wpid"):
            array.loc["Wpidowed"] = 1
        if any(((x.__contains__('div'), x.__contains__('sep')))):
            array.loc["Divorced_or_Sep"] = 1
        return array


    @key_error_return_none
    def get_demographics_array(self, pid):
        x = self.df.loc[[pid],:]

        race_array = self\
        .race_ohe(' '.join(x.loc[:, self.race_col]))

        marital_status_array = self\
        .marital_status_ohe(' '.join(x.loc[:, self.marital_stat_col]))

        gender_array = self\
        .gender_ohe(' '.join(x.loc[:, self.gender_col]))

        return pd.concat([race_array, gender_array, marital_status_array], axis=1).max(axis=1)

    @key_error_return_none
    def get_age_at_dt(self, pid, dt=datetime.today()):
        logger.debug(F'using age as of {dt}')
        x = self.df.loc[[pid],self.age_col].max()
        return pd.to_datetime(dt).year - x

    def get_demographics_tags(self, pid):
        x = self.df.loc[[pid], :]
        d = dict()
        d[self.race_col] = ' '.join(x.loc[:, self.race_col])
        d[self.marital_stat_col] = ' '.join(x.loc[:, self.marital_stat_col])
        d[self.gender_col] = ' '.join(x.loc[:, self.gender_col])
        d[self.pid_col] = pid
        return d

    def transform(self, pids, ):
        first_example = self.get_demographics_array(pids[0])
        cols = first_example.index
        results = np.zeros((len(pids), len(cols)))
        for i, pid in enumerate(pids):
            results[i, :] =  self.get_demographics_array(pid)
        results = pd.DataFrame(results, columns=cols)
        results.index = pids
        return results

    @key_error_return_none
    def get_svi_flags(self, pid):
        raise NotImplementedError

    @key_error_return_none
    def get_svi_array(self, pid):
        raise NotImplementedError

class Geograpics:
    def __init__(self, df):
        self.pid_col = 'DEID'
        self.fips_col = "FIPS"
        self.df = df.sort_values(by=self.pid_col)
        self.df = self.df.set_index(self.pid_col)
        self.df.loc[:, self.fips_col] = self.df.loc[:,  self.fips_col].astype(str)
        data_dir = os.environ['CANCER_UPTAKE_DATA_HOME']
        path= F"{data_dir}//SVI2018_US.csv"
        self.svi_df = pd.read_csv(path)
        self.svi_df.loc[:, self.fips_col ] = self.svi_df.loc[:, self.fips_col ].astype(str).str.replace('.0', '', regex=False).str.strip()
        self.svi_df = self.svi_df.set_index(self.fips_col )
        self.theme_flag_cols = ['F_THEME1', 'F_THEME2', 'F_THEME3','F_THEME4' ]
        self.flag_cols = ['F_POV', 'F_UNEMP', 'F_PCI', 'F_NOHSDP', 'F_AGE65', 'F_AGE17', 'F_DISABL', 'F_SNGPNT',
                       'F_MINRTY',  'F_LIMENG', 'F_MUNIT', 'F_MOBILE', 'F_CROWD', 'F_NOVEH', 'F_GROUPQ']

        self.theme_rpl_cols = ['RPL_THEME1', 'RPL_THEME2','RPL_THEME3',  'RPL_THEME4']
        self.epl_cols = ['EPL_POV', 'EPL_UNEMP', 'EPL_PCI', 'EPL_NOHSDP', 'EPL_AGE65', 'EPL_AGE17', 'EPL_DISABL',
                         'EPL_SNGPNT', 'SPL_THEME2', 'RPL_THEME2', 'EPL_MINRTY', 'EPL_LIMENG', 'SPL_THEME3',
                         'EPL_MUNIT', 'EPL_MOBILE', 'EPL_CROWD', 'EPL_NOVEH', 'EPL_GROUPQ']
        self.state_col = 'STATE'
        self.county_col = 'COUNTY'
        self.county_fips_col = 'STCNTY'

        self.theme_dict = {"RPL_THEME1":"Socioeconomic",
                           "RPL_THEME2": 'Household Composition/Disabilit',
                           "RPL_THEME3": "Minority Status/Language",
                           "RPL_THEME4": "Housing Type/Transportation"}


        logger.debug(F'screening tests loaded with {self.df.shape[0]} rows')
        logger.debug(F'svi data loaded with {self.svi_df.shape} from  {path}')



    def get_theme_flags(self,  pid=None, fips=None):
        svi = self.query_svi(pid, fips)
        return svi.loc[self.theme_flag_cols].astype(int)

    def get_epl(self, pid=None, fips=None):
        svi = self.query_svi(pid, fips)
        return svi.loc[self.epl_cols].astype(float)

    def get_theme(self, pid=None, fips=None):
        svi = self.query_svi(pid, fips)
        return svi.loc[ self.theme_rpl_cols].astype(float)

    def get_flags(self,  pid=None, fips=None):
        svi = self.query_svi(pid, fips)
        return svi.loc[self.flag_cols ].astype(int)

    def get_state(self, pid=None, fips=None):
        svi = self.query_svi(pid, fips)
        return svi.loc[self.state_col]

    def get_county(self, pid=None, fips=None):
        svi = self.query_svi(pid, fips)
        return svi.loc[self.county_col]
    def get_county_fips(self, pid=None, fips=None):
        svi = self.query_svi(pid, fips)
        return svi.loc[self.county_fips_col]
    def query_svi(self, pid=None, fips=None):
        if fips is None:
            fips = self.df.loc[[pid], self.fips_col].astype(str).values[0]
            fips = fips.replace(".0", '')
            logger.debug(F'found fips {fips} for id {pid}')

        try:
            results = self.svi_df.loc[[fips], :]
            if isinstance(results, type(pd.DataFrame([]))):
                results = results.iloc[0 , :]
            return results
        except KeyError:
            logger.warn(F'fips {fips} location no found in svi')
            return None

class CPT:
    def __init__(self, df):
        self.pid_col = 'DEID'
        self.date_col = 'CPT_DATE'
        self.code_col = 'CPT_CODE'
        self.desc_col = 'PROC_NAME'
        self.df = df.set_index(self.pid_col)
        self.df = self.df.sort_index()
        self.df.loc[:, self.date_col] = pd.to_datetime(self.df.loc[:, self.date_col])
        self.df.loc[:, self.code_col] = self.df.loc[:, self.code_col].str.lower()
        self.df.loc[:, self.desc_col] = self.df.loc[:, self.desc_col].str.lower()

    @key_error_return_dict
    def query_dict(self, pid, dt=datetime.today()):
        x = self.df.loc[[pid], :].copy()
        x = x.loc[(x.loc[:, self.date_col] <= dt), :]
        return x.to_dict('series')


    @key_error_return_none
    def first_cpt_dt(self, pid, test_type=None):
        x = self.df.loc[[pid], :].copy()
        if test_type:
            index =  x.loc[:, self.desc_col].fillna('').str.contains(test_type.lower())
            x = x.loc[index, :]
        else:
            pass
        date = x.loc[:, self.date_col].min()
        if np.isnan(date.year):
            return None
        else:
            return date.date()

    @key_error_return_array
    def get_cpts(self, pid, test_type=None, dt=datetime.today(),max_days_prior=n_days_prior):
        dt = pd.to_datetime(dt)
        x = self.df.loc[[pid], :].copy()
        x = x.loc[x.loc[:, self.date_col] < pd.to_datetime(dt), :]
        index_within_days = (dt - x.loc[:, self.date_col] )/np.timedelta64(1, 'D') <= max_days_prior
        x = x.loc[index_within_days, :]
        if test_type:
            index =  x.loc[:, self.desc_col].fillna('').str.contains(test_type.lower())
            x = x.loc[index, :]
        else:
            pass
        results = np.unique(x.loc[:, self.desc_col])
        if len(results) > 0:
            return results
        else:
            return np.array([])


class Billing:
    def __init__(self, df):
        self.pid_col = 'DEID'
        self.date_col = 'DX_DATE'
        self.code_col = 'DX_CODE'
        self.desc_col = 'DX_NAME'
        self.df = df.set_index(self.pid_col)
        self.df = self.df.sort_index()
        self.df.loc[:, self.date_col] = pd.to_datetime(self.df.loc[:, self.date_col])
        self.df.loc[:, self.code_col] = self.df.loc[:, self.code_col].str.lower()
        self.df.loc[:, self.desc_col] = self.df.loc[:, self.desc_col].str.lower()

    def query_dict(self, pid, dt=datetime.today()):
        x = self.df.loc[[pid], :].copy()
        x = x.loc[(x.loc[:, self.date_col] <= dt), :]
        return x.to_dict('series')

    @key_error_return_array
    def get_codes(self, pid, code_type=None, dt=datetime.today(),max_days_prior=n_days_prior):
        dt = pd.to_datetime(dt)
        x = self.df.loc[[pid], :].copy()
        x = x.loc[x.loc[:, self.date_col] < pd.to_datetime(dt), :]
        index_within_days = (dt - x.loc[:, self.date_col] )/np.timedelta64(1, 'D') <= max_days_prior
        x = x.loc[index_within_days, :]
        if code_type:
            index =  x.loc[:, self.desc_col].fillna('').str.contains(code_type.lower())
            x = x.loc[index, :]
        else:
            pass
        results = np.unique(x.loc[:, self.code_col])
        if len(results) > 0:
            return results
        else:
            return np.array([])

    def get_elix_array(self, pid,  dt=datetime.today(),max_days_prior=n_days_prior):
        codes = self.get_codes(pid, dt=dt, max_days_prior=max_days_prior)
        logger.debug(F'detected codes {codes }')

        results = comorbidity_from_array(str(codes).split(' '))
        try:
            results = results.drop('# Comorbidities', axis=1)
        except KeyError:
            pass
        return results.max(axis=0)

    @key_error_return_array
    def get_condtion_tags(self, pid, dt=datetime.today(),max_days_prior=n_days_prior):
        codes = self.get_codes(pid, dt=dt, max_days_prior=max_days_prior)
        try:
            return get_condtion_tags_icd10(' '.join(codes))
        except TypeError:
            return np.array([])


class Problems:
    def __init__(self, df):
        self.pid_col = 'DEID'
        self.date_col = 'ENTRY_DATE'
        self.code_col = 'DX_CODE'
        self.desc_col = 'DX_NAME'
        self.status_col = 'PROBLEM_STATUS'
        self.df = df.set_index(self.pid_col)
        self.df = self.df.sort_index()
        self.df.loc[:, self.date_col] = pd.to_datetime(self.df.loc[:, self.date_col])
        self.df.loc[:, self.code_col] = self.df.loc[:, self.code_col].astype(str).str.lower()
        self.df.loc[:, self.desc_col] = self.df.loc[:, self.desc_col].str.lower()
        self.df.loc[:, self.status_col] = self.df.loc[:, self.status_col].str.lower()
        self.ner = None
    def query(self, pid,  dt=datetime.today()):
        dt = pd.to_datetime(dt)
        try:
            x = self.df.loc[[pid], :].copy().dropna(subset=[self.desc_col ], axis=0)
            x = x.loc[x.loc[:, self.date_col].dt.date <= pd.to_datetime(dt).date(), :]
            return x
        except KeyError:
            return pd.DataFrame()
    @key_error_return_dict
    def query_dict(self, pid, dt=datetime.today()):
        x = self.df.loc[[pid], :].copy()
        x = x.loc[(x.loc[:, self.date_col] <= dt), :]
        return x.to_dict('series')

    def _set_ner(self):
        from CancerUtils.icd_from_raw_text import TextToIcd9
        self.ner = TextToIcd9().fit(10)


    @key_error_return_array
    def get_codes(self, pid, code_type=None, dt=datetime.today(),max_days_prior=n_days_prior):
        dt = pd.to_datetime(dt)
        x = self.df.loc[[pid], :].copy().dropna(subset=[self.code_col], axis=0)
        x = x.loc[x.loc[:, self.date_col] < pd.to_datetime(dt), :]
        x = x.loc[x.loc[:, self.status_col].str.contains('del"') == False, :]
        index_within_days = (dt - x.loc[:, self.date_col] )/np.timedelta64(1, 'D') <= max_days_prior
        x = x.loc[index_within_days, :]
        x =  x.loc[x.loc[:, self.code_col].str.contains('nan') == False, :]
        if code_type:
            index =  x.loc[:, self.desc_col].fillna('').str.contains(code_type.lower())
            x = x.loc[index, :]
        else:
            pass
        results = np.unique(x.loc[:, self.code_col])
        if len(results) > 0:
            return results
        else:
            return np.array([])

    @key_error_return_array
    def get_uncoded_problems(self, pid, code_type=None, dt=datetime.today(),max_days_prior=n_days_prior):
        dt = pd.to_datetime(dt)
        x = self.df.loc[[pid], :].copy().dropna(subset=[self.code_col], axis=0)
        x = x.loc[x.loc[:, self.date_col] < pd.to_datetime(dt), :]
        x = x.loc[x.loc[:, self.status_col].str.contains('del"') == False, :]
        index_within_days = (dt - x.loc[:, self.date_col] )/np.timedelta64(1, 'D') <= max_days_prior
        x = x.loc[index_within_days, :]
        x =  x.loc[x.loc[:, self.code_col].str.contains('nan'), :]
        if code_type:
            index =  x.loc[:, self.desc_col].fillna('').str.contains(code_type.lower())
            x = x.loc[index, :]
        else:
            pass
        results = np.unique(x.loc[:, self.desc_col])
        if len(results) > 0:
            return results
        else:
            return np.array([])

    @key_error_return_array
    def get_uncoded_cancer_tags(self, pid, code_type=None, dt=datetime.today(), max_days_prior=n_days_prior):
        problems = pd.Series(self.get_uncoded_problems(pid, code_type, dt, n_days_prior))
        tags = problems.apply(get_cancer_history_tags).values.ravel()
        return np.unique(list(chain.from_iterable(tags)))

    @key_error_return_array
    def get_codes_from_uncoded_problems(self, pid, code_type=None, dt=datetime.today(),max_days_prior=n_days_prior, min_sim = .9):
        dt = pd.to_datetime(dt)
        x = self.df.loc[[pid], :].copy().dropna(subset=[self.code_col], axis=0)
        x = x.loc[x.loc[:, self.date_col] < pd.to_datetime(dt), :]
        x = x.loc[x.loc[:, self.status_col].str.contains('delet') == False, :]
        index_within_days = (dt - x.loc[:, self.date_col] )/np.timedelta64(1, 'D') <= max_days_prior
        x = x.loc[index_within_days, :]
        x = x.loc[x.loc[:, self.code_col].str.contains('nan') == False, :]
        if code_type:
            index = x.loc[:, self.desc_col].fillna('').str.contains(code_type.lower())
            x = x.loc[index, :]
        else:
            pass
        descriptions = np.unique(x.loc[:, self.desc_col])

        if len(descriptions) > 0:
            if isinstance(self.ner, type(None)):
                self._set_ner()
            results = [self.ner.get_nearest_icd9(text, min_sim=min_sim)['code'] for text in descriptions]
            results = [r for r in results if r != None]
            return np.unique(results)
        else:
            return np.array([])
    @key_error_return_array
    def get_condtion_tags(self, pid,  dt=datetime.today()):
        x = self.query(pid, dt)
        results = x.loc[:, self.desc_col].apply(get_condtion_tags_text)
        results = np.unique(list(chain.from_iterable(results)))
        return results


class Insurance:
    def __init__(self, df):
        self.pid_col = 'DEID'
        self.date_col = 'VISIT_YEAR'
        self.payer_col = 'PAYOR_NAME'
        self.age_col = "AGE_AT_VISIT"
        self.df = df
        self.df.loc[:, self.date_col] = pd.to_numeric(self.df.loc[:, self.date_col])
        self.df.loc[:, self.pid_col] = self.df.loc[:, self.pid_col].astype(int)
        self.df = df.set_index(self.pid_col)
        self.df = self.df.sort_index()

    @key_error_return_dict
    def query_dict(self, pid, dt=datetime.today()):
        x = self.df.loc[[pid], :].copy()
        x = x.loc[(x.loc[:, self.date_col] <= dt), :]
        return x.to_dict('series')

    def query(self, pid):
        x = self.df.loc[[pid], :].copy()
        return x

    def get_insurance(self, pid, dt=datetime.today()):
        dt = pd.to_datetime(dt)
        try:
            x = self.query(pid)
        except KeyError:
            logger.debug(F'Failed to find key {pid} in insurance table')
            return "unknown"

        x.loc[:, 'date_diff'] = np.abs(dt.date().year - x.loc[:, self.date_col])
        x = x.sort_values(by='date_diff')
        return ' '.join(x.tail(1).loc[:, self.payer_col])



    def get_insurance_array(self, ppid, dt=datetime.today() ):
        dt = pd.to_datetime(dt)
        insurance = self.get_insurance(ppid, dt)
        d = {}
        for key, func in insurance_tag_dict.items():
            d[key] = func(insurance)
        return pd.Series(d.values(), index=d.keys())


class FamilyHistory:
    def __init__(self, df):
        self.pid_col = 'DEID'
        self.date_col = 'FHX_CONTACT_DATE'
        self.medical_hx_col = 'MEDICAL_HX'
        self.relation_col = "RELATION"
        self.age_col = "AGE_OF_ONSET"
        self.df = df
        self.df.loc[:, self.medical_hx_col] = self.df.loc[:, self.medical_hx_col].str.lower().str.strip()
        self.df.loc[:, self.relation_col] = self.df.loc[:, self.relation_col].str.lower().str.strip()
        self.df.loc[:, self.date_col] = pd.to_datetime(self.df.loc[:, self.date_col])
        self.df.loc[:, self.pid_col] = self.df.loc[:, self.pid_col].astype(int)
        self.df.loc[:,  self.age_col] = pd.to_numeric( self.df.loc[:,  self.age_col])
        self.df = df.set_index(self.pid_col)
        self.df = self.df.sort_index()

    @key_error_return_dict
    def query_dict(self, pid, dt=datetime.today()):
        x = self.df.loc[[pid], :].copy()
        x = x.loc[(x.loc[:, self.date_col] <= dt), :]
        return x.to_dict('series')

    def query_hist(self, pid,  dt=datetime.today()):
        dt = pd.to_datetime(dt)
        x = self.df.loc[[pid], :].copy().dropna(subset=[self.medical_hx_col], axis=0)
        x = x.loc[x.loc[:, self.date_col].dt.date <= pd.to_datetime(dt).date(), :]
        return x

    @key_error_return_array
    def relatives_with_early_onset_cancer(self, pid,dt=datetime.today(),  age=50):
        x = self.query_hist(pid,  dt)
        result = x.loc[((x.loc[:, self.relation_col].apply(chd['first_degree_relative'])) &
                           (x.loc[:, self.medical_hx_col].str.lower().str.contains('cancer')) &
                           (x.loc[:, self.age_col] < age )), :]
        return np.unique(result.loc[:, self.relation_col])

    @key_error_return_array
    def cancer_types_in_relatives_early_onset(self, pid,dt=datetime.today(),  age=50):
        x = self.query_hist(pid,  dt)
        result = x.loc[(x.loc[:, self.relation_col].apply(chd['first_degree_relative'])) &
                           (x.loc[:, self.medical_hx_col].str.lower().str.contains('cancer')) &
                           (x.loc[:, self.age_col] < age ), :]
        return np.unique(result .loc[:, self.medical_hx_col])
    @key_error_return_array
    def cancer_types_confirmed_negative_history(self, pid, dt=datetime.today()):
        x = self.query_hist(pid, dt)
        result = x.loc[(x.loc[:, self.medical_hx_col].str.lower().str.contains('cancer')) &
                           (x.loc[:, self.relation_col].str.lower().str.contains('neg hx')), :]
        return np.unique(result.loc[:, self.medical_hx_col])

    @key_error_return_array
    def relatives_with_breast_cancer(self, pid, dt=datetime.today()):
        x = self.query_hist(pid, dt)
        result = x.loc[(x.loc[:, self.medical_hx_col].str.lower().str.contains('breast')) &
                        (x.loc[:, self.relation_col].str.lower().str.contains('neg hx') == False), :]
        return np.unique(result .loc[:, self.relation_col])

    @key_error_return_array
    def cancer_types_in_first_degree_relatives(self,  pid, dt=datetime.today()):
        x = self.query_hist(pid,  dt)
        result = x.loc[(x.loc[:, self.relation_col].apply(chd['first_degree_relative'])) &
                           (x.loc[:, self.medical_hx_col].str.lower().str.contains('cancer')), :]
        return np.unique(result .loc[:, self.medical_hx_col])
    @key_error_return_array
    def cancer_types_confirmed_in_relatives(self,  pid, dt=datetime.today()):
        x = self.query_hist(pid,  dt)
        result = x.loc[x.loc[:, self.medical_hx_col].str.lower().str.contains('cancer'), :]
        return np.unique(result .loc[:, self.medical_hx_col])

    @key_error_return_array
    def get_conditon_tags(self,  pid, dt=datetime.today()):
        x = self.query_hist(pid,  dt)
        results = x.loc[:, self.medical_hx_col] + ' ' +  self.df.loc[:, self.relation_col]
        results = results.astype(str).apply(get_condtion_tags_text)
        results = np.unique(list(chain.from_iterable(results)))
        return results

class PersonalHistory:
    def __init__(self, df):
        self.pid_col = 'DEID'
        self.date_col = 'MHX_CONTACT_DATE'
        self.medical_hx_col = 'DX_NAME'
        self.dx_date_col = 'MEDICAL_HX_DATE'
        self.df = df
        self.df.loc[:, self.medical_hx_col] = self.df.loc[:, self.medical_hx_col].str.lower().str.strip()
        self.df.loc[:, self.date_col] = pd.to_datetime(self.df.loc[:, self.date_col])
        self.df.loc[:, self.pid_col] = self.df.loc[:, self.pid_col].astype(int)
        self.df.loc[:, self.dx_date_col ] = self.df.loc[:, self.dx_date_col ].astype(str)

        self.df = df.set_index(self.pid_col)
        self.df = self.df.sort_index()

    @key_error_return_dict
    def query_dict(self, pid, dt=datetime.today()):
        x = self.df.loc[[pid], :].copy()
        x = x.loc[(x.loc[:, self.date_col] <= dt), :]
        return x.to_dict('series')

    @staticmethod
    def year_from_str(s):
        try:
            year = re.search("\d{4}",str(s)).group()
            year = pd.to_numeric(year)
            return year
        except AttributeError:
            return np.nan

    def query_hist(self, pid,  dt=datetime.today()):
        dt = pd.to_datetime(dt)
        try:
            x = self.df.loc[[pid], :].copy().dropna(subset=[self.medical_hx_col], axis=0)
            x = x.loc[x.loc[:, self.date_col].dt.date <= pd.to_datetime(dt).date(), :]
            return x
        except KeyError:
            return pd.DataFrame()

    @key_error_return_array
    def cancer_types_in_family(self, pid,  dt=datetime.today()):
        x = self.query_hist(pid,  dt)
        result = x.loc[(x.loc[:, self.medical_hx_col].apply(chd['family_history_of_cancer'])), :]
        return np.unique(result .loc[:, self.medical_hx_col].apply(strip_history))

    @key_error_return_array
    def cancer_types_personal_hist(self, pid,  dt=datetime.today()):
        x = self.query_hist(pid, dt)
        result = x.loc[(x.loc[:, self.medical_hx_col].apply(chd['is_cancer'])) &
                       (x.loc[:, self.medical_hx_col].apply(condition_tag_dict['family_reference']) == False), :]
        return np.unique(result.loc[:, self.medical_hx_col].apply(strip_history))
    @key_error_return_none
    def breast_cancer_personal_hist(self, pid,  dt=datetime.today()):
        x = self.query_hist(pid, dt)
        result = x.loc[:, self.medical_hx_col].apply(condition_tag_dict['breast_cancer'])
        return any(result)

    @key_error_return_array
    def cancer_types_more_than_5y(self, pid,  dt=datetime.today()):
        x = self.query_hist(pid, dt)
        year= dt.date().year
        result = x.loc[(x.loc[:, self.medical_hx_col].apply(chd['is_cancer'])) &
                       (x.loc[:, self.medical_hx_col].apply(condition_tag_dict['family_reference']) == False) &
                       (year - x.loc[:, self.dx_date_col].apply(self.year_from_str) > 5), :]
        return np.unique(result.loc[:, self.medical_hx_col].apply(strip_history))

    @key_error_return_array
    def get_condtion_tags(self, pid,  dt=datetime.today()):
        x = self.query_hist(pid, dt)
        results = x.loc[:, self.medical_hx_col].apply(get_condtion_tags_text)
        results = np.unique(list(chain.from_iterable(results)))
        return results


def _test_PersonalHistory():
    data_dir = os.environ['CANCER_UPTAKE_DATA_HOME']
    path = F"{data_dir}/Sparc15830-0006_Results_v5.xlsx"
    df = pd.read_excel(path, sheet_name="Grid Results (9)")
    logger.setLevel('DEBUG')
    p = PersonalHistory(df)
    assert len(p.cancer_types_personal_hist(29) ) == 2
    logger.debug('test dx year filters ..')
    assert p.cancer_types_more_than_5y(294)  == ['prostate cancer']
    assert(p. cancer_types_in_family(302)) == ['breast cancer']
    p.cancer_types_personal_hist(-5)
    assert p.breast_cancer_personal_hist(48)
    assert 'breast_cancer' in p.get_condtion_tags(95)
    logger.info('testings PersonalHistory  class ...')


def _test_Geographics():
    logger.setLevel('DEBUG')
    logger.info('testings Geographics ...')
    data_dir = os.environ['CANCER_UPTAKE_DATA_HOME']
    path = F"{data_dir}/Sparc15830-0006_Results_v5.xlsx"
    df = pd.read_excel(path, sheet_name="Grid Results (2)")
    g = Geograpics(df)
    assert g.get_county(1) is not None
    assert g.get_epl(1).shape[0] == 18
    assert g.get_theme_flags(1).shape[0] ==4
    assert g.get_county_fips(1) != None
    assert g.get_state(1) != None
    assert g.get_flags(1).shape[0] == 15
    logger.debug('Geographic test completed  ')


def _test_FamilyHistory():
    data_dir = os.environ['CANCER_UPTAKE_DATA_HOME']
    path = F"{data_dir}/Sparc15830-0006_Results_v5.xlsx"
    logger.setLevel('DEBUG')
    df = pd.read_excel(path, sheet_name="Grid Results (10)")
    f = FamilyHistory(df)

    logger.info('testings FamilyHistory  class ...')
    assert  len(f.relatives_with_early_onset_cancer(66)) == 1
    assert f.cancer_types_in_relatives_early_onset(66) == ['breast cancer']
    assert len(f.cancer_types_in_first_degree_relatives(1)) == 0
    assert len(f.cancer_types_in_first_degree_relatives(4)) == 2
    assert f.cancer_types_in_first_degree_relatives(8) == ['throat cancer']
    assert len(f.relatives_with_breast_cancer(4)) == 2
    f.cancer_types_confirmed_negative_history(22) ==['prostate cancer']
    print(f.get_conditon_tags(14))


def _test_ScreeningTests():
    data_dir = os.environ['CANCER_UPTAKE_DATA_HOME']
    path = F"{data_dir}/Sparc15830-0006_Results_v5.xlsx"
    df = pd.read_excel(path, sheet_name="Grid Results (8)")
    logger.setLevel('DEBUG')
    logger.info('testings SCreeningTests class ...')
    s = ScreeningTests(df)
    assert s.first_ordered_dt(14) == pd.to_datetime('2016-07-06 08:19:00')
    assert s.first_ordered_dt(-1) is None
    assert s.first_completed_dt(14) == pd.to_datetime('2016-07-06 00:00:00')
    assert s.first_sent_dt(14) is None
    assert s.first_sent_dt(5, test_type='colo') == pd.to_datetime('2017-09-27 12:38:00')
    assert s.days_to_complete(549, "mam") == 28
    assert s.days_to_complete(14) == 0
    assert s.days_to_complete(-14) is None
    assert s.days_to_send(134, "mam")== 0
    assert s.case_control_detection(14, "mam", ref_dt='2019-12-31', mask_same_day=True)['case_control'] == 'mask'
    assert s.case_control_detection(14, "mam", ref_dt='2019-12-31', mask_same_day=False)['case_control'] == 'control'
    assert s.case_control_detection(39, "mam", ref_dt='2019-12-31')['case_control']  == 'control'
    assert s.case_control_detection(72, "mam", ref_dt='2019-12-31')['case_control']  == 'case'
    assert s.case_control_detection(91, "mam", ref_dt='2019-12-31')['case_control']  == 'case'
    assert s.case_control_detection(91, "mam", ref_dt='2019-12-31')['case_control']  == 'case'
    assert s.case_control_detection(119, "mam", ref_dt='2019-12-31')['case_control']  == 'control'
    assert s.case_control_detection(134, "mam", ref_dt='2019-12-31')['case_control']  == 'mask'
    assert s.case_control_detection(-1, "mam", ref_dt='2019-12-31')['case_control']  == 'mask'
    assert s.case_control_detection(5, "mam", mask_same_day=False)['case_control']   == 'control'
    assert s.case_control_detection(5, "mam", mask_same_day=True)['case_control']   == 'mask'
    assert s.case_control_detection(5, "colo", mask_same_day=True)['case_control']   == 'mask'
    logger.debug('running bulk test...')
    x = pd.Series(np.unique(df.DEID))
    x.head(50).apply(lambda x: s.case_control_detection(x, 'mam')['case_control'])
    print(s.query_dict(14))
    logger.info('query test module completed')


def _test_Demogaphics():
        logger.setLevel('DEBUG')
        logger.info('testings Demographics class ...')
        data_dir = os.environ['CANCER_UPTAKE_DATA_HOME']
        path = F"{data_dir}/Sparc15830-0006_Results_v5.xlsx"
        df = pd.read_excel(path, sheet_name="Grid Results (2)")
        d = Demographics(df)
        assert d.race_ohe('black or african american').iloc[1]==1
        assert d.race_ohe('white or caucasian').sum()==1
        assert d.race_ohe('asian').iloc[2]==1
        assert d.race_ohe('black or african american').sum() == 1
        assert d.gender_ohe("male").iloc[1] == 1
        assert d.gender_ohe("female").iloc[0] == 1
        assert d.gender_ohe("toaster").iloc[2] == 1
        assert d.gender_ohe('female').sum() == 1
        assert d.marital_status_ohe("married").iloc[0]==1
        assert d.marital_status_ohe("seperated").iloc[2]==1
        assert d.marital_status_ohe("single").iloc[1]==1
        assert d.marital_status_ohe('LEGALLY SEPARATED').sum() ==1
        assert d.get_age_at_dt(1, '2022-01-01') == 24
        logger.debug(F'Demmophaics Array {d.get_demographics_array(1).to_dict()}')
        assert d.get_demographics_array(1).sum() == 3
        pids = pd.Series(np.unique(df.DEID))
        print(d.query_dict(1))
        logger.info('demographics class testing completed ')


def _test_CPT():
    logger.setLevel('DEBUG')
    logger.info('testings CPT class ...')
    data_dir = os.environ['CANCER_UPTAKE_DATA_HOME']
    path = F"{data_dir}/Sparc15830-0006_Results_v5.xlsx"
    df = pd.read_excel(path, sheet_name="Grid Results (11)")
    c = CPT(df)
    assert c.first_cpt_dt(82, test_type='breast') == pd.to_datetime('2018-04-05').date()
    assert c.first_cpt_dt(3200, test_type='breast.+tomos') == pd.to_datetime('2019-02-28').date()
    assert len(c.get_cpts(5600, test_type='breast', dt='2018-12-31'))==2
    assert len(c.get_cpts(12084, test_type='breast', dt='2018-12-31'))==2
    print(c.query_dict(824))
    logger.info('CPT testing completed')


def _test_Billing():
    logger.setLevel('DEBUG')
    logger.info('testings Billing class ...')
    data_dir = os.environ['CANCER_UPTAKE_DATA_HOME']
    path = F"{data_dir}/Sparc15830-0006_Results_v5.xlsx"
    df = pd.read_excel(path, sheet_name="Grid Results (6)")
    b = Billing(df)
    assert len(b.get_codes(1, dt="2020-01-01", max_days_prior=1085))==7
    assert b.get_elix_array(34, dt="2020-01-01", max_days_prior=365*10 ).sum()==2
    print( b.get_condtion_tags(34, dt="2020-01-01", max_days_prior=365*10 ))
    assert len(b.get_condtion_tags(34)) > 0
    print(b.query_dict(34))
    logger.info('Billing testing completed')


def _test_Problems():
    logger.setLevel('DEBUG')
    logger.info('testings Problems class ...')
    data_dir = os.environ['CANCER_UPTAKE_DATA_HOME']
    path = F"{data_dir}/Sparc15830-0006_Results_v5.xlsx"
    df = pd.read_excel(path, sheet_name="Grid Results (7)")
    p = Problems(df)
    assert len(p.get_codes(18, code_type=None, dt="2020-01-01")) == 10
    assert len(p.get_uncoded_problems(18, code_type=None, dt="2020-01-01"))==3
    print(p.get_codes_from_uncoded_problems(4,  dt="2020-01-01"))
    print(p.get_uncoded_cancer_tags(4, dt="2020-01-01" ))
    print(p.query_dict(18))
    assert len(p.get_condtion_tags(18)) > 0
    logger.debug("Problem Class tests completed ")


def _test_Insturance():
    logger.setLevel('DEBUG')
    logger.info('testings Insurance class ...')
    data_dir = os.environ['CANCER_UPTAKE_DATA_HOME']
    path = F"{data_dir}/Sparc15830-0006_Results_v5.xlsx"
    df = pd.read_excel(path, sheet_name="Grid Results (3)")
    i = Insurance(df)
    assert i.get_insurance(34, dt='2017-01-01') ==  "BCBS OF SC"
    assert i.get_insurance(491, dt='2017-01-01') == "UNITED HEALTHCARE MEDICARE SOLUTIONS"
    assert i.get_insurance_array(491,dt='2017-01-01').sum() == 2
    print(i.query_dict(14))
    logger.debug("Insurance class test completd")
def _test():
    logger.info("Testing Query module ... ")
    _test_FamilyHistory()
    _test_PersonalHistory()
    _test_Geographics()
    _test_Insturance()
    _test_ScreeningTests()
    _test_Demogaphics()
    _test_CPT()
    _test_Billing()
    _test_Problems()
    logger.info("Query module testing complete")





if __name__ == "__main__":
    logger.setLevel("DEBUG")
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', help='test method for module', action='store_true')
    args = parser.parse_args()
    if args.test:
        _test()
    else:
        pass