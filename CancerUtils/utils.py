import pkg_resources
import re
import pandas as pd
import numpy as np
import pickle
import logging
from CancerUtils.setup_logger import logger

_pkg_name = 'CancerUtils'

def load_resource(path):
    stream = pkg_resources.resource_string(_pkg_name, path)
    results =str(stream).split('\\n')
    results = [item.strip() for _, item in enumerate(results) if len(item)>1]
    return results

def load_pickeled_resource(resource_name):
    return pickle.load(
        pkg_resources.resource_stream(_pkg_name, resource_name))

def key_error_return_none(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            logger.debug('key error return None wrapper envoked')
            return None
    return wrapper


def value_error_return_none(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            logger.debug('value error return None wrapper envoked')
            return None
    return wrapper


def key_error_return_array(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            logger.debug('key error return array wrapper envoked')
            return np.array([])
    return wrapper

def key_error_return_dict(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            logger.debug('key error return dict wrapper envoked')
            return {}
    return wrapper


def apply_with_tokenizer(func):
    def wrapper(*args, **kwargs):
        try:
            v = args[0]
        except IndexError:
            v = kwargs['s']
        v = v.strip()
        return any([func(s) for s in v.split(' ')])
    return wrapper

def coerce_to_string(func):
    def wrapper(*args, **kwargs):
        try:
            v = args[0]
        except IndexError:
            v = kwargs['s']
        if isinstance(v, type(None)):
            v = ''
        if isinstance(v, type(np.array([1]))):
            v = ' '.join(v.astype(str))
        if isinstance(v, type(pd.Series(1).astype(str))):
            v = ' '.join(v.astype(str))
        if isinstance(v, type(list())):
            v = ' '.join(v)

        return func(v)

    return wrapper


def logger_inputs_and_outputs(func):
    def wrapper(*args, **kwargs):
        results = func(*args, **kwargs)
        try:
            msg = str(func) + ' \n args: ' + str(args) + '\n kwargs: '+ str(kwargs) + '\n results: ' +  str(results)
            logger.debug(msg)
        except:
            pass
        return results
    return wrapper

