
import os
import numpy as np
import pickle
import pandas as pd
import re

from sklearn.neighbors import NearestNeighbors

from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem import WordNetLemmatizer
import stanza

from CancerUtils.setup_logger import logger
from CancerUtils.utils import load_pickeled_resource, load_resource

from CancerUtils.text import condition_tag_dict, get_condtion_tags, replace_history

'''
from CancerUtils.icd_from_raw_text import TextToIcd9
nn = TextToIcd9().fit()
text = 'solid tumor in left breast'
results = nn.get_nearest_icd9(text)
print(F'*** Dectected {text}, {results}')


'''



class TextToIcd9:
    def __init__(self):
        self.nlp = None
        self.lemmatizer = None
        self._icd9_all = None
        self._codes = None
        self.word_vectors = None

    def _load_word_vectors(self):
        logger.info('loading word vectors and ICD9s ...')
        self._icd9_all = load_resource('resources/CMS32_DESC_LONG_DX.txt')
        self._icd9_all[0] = self._icd9_all[0][2:]
        self._codes = pd.Series([str(' '.join(v.split(' ')[1:])) for v in self._icd9_all],
                            index = [v.split(' ')[0] for v in self._icd9_all])
        self._codes = self._codes.str.replace('\\r', '').str.replace('\r', '').str.strip()
        logger.info(F'icd9 data loaded with {self._codes.shape[0]} codes from pkg_resources')
        self.word_vectors = {}
        for line in load_resource('resources/word_vectors.csv')[1:]:
            line_split = line.split(',')

            vectors = [v.replace('\\r', '').replace('\r', '') for v in line_split[1:]]

            self.word_vectors[line_split[0]] = pd.to_numeric(vectors)

            logger.info('word vectors loaded')


    def _load_nlp_engine(self):
        logger.info('loading nlp engine ... ')
        self.n_dims = len(list(self.word_vectors.values())[0])
        self.lemmatizer = WordNetLemmatizer()
        logger.debug(F'loaded: {len(self.word_vectors.items())}  word vectors of dim: {self.n_dims} ')
        try:
            self.nlp = stanza.Pipeline(lang='en', package='anatem',processors={'tokenize': 'spacy', "ner":"anatem"})
        except:
            stanza.download(lang="en",package=None,processors={"ner":"anatem"})
            self.nlp = stanza.Pipeline(lang='en', package='anatem',processors={'tokenize': 'spacy', "ner":"anatem"})
        self.stop_words = set(['a','an','and','but','how','in','on','or','the','what','will','of', 'this', 'is', 'were', 'was'])

    def fit(self, n_neighbors=10):
        if isinstance(self.word_vectors, type(None)):
            self._load_word_vectors()

        if isinstance(self.nlp, type(None)):
            self._load_nlp_engine()

        features = np.vstack(self._codes.apply(self.get_document_vector))
        logger.debug(F'fitting knn with data shape {features.shape}')
        self._nbrs = NearestNeighbors(n_neighbors=n_neighbors, algorithm='ball_tree').fit(features)
        return self

    def get_problems(self, text):
        doc = self.nlp(text.lower())
        problems = []
        for sentence in doc.sentences:
            for d in sentence.entities:
                problems.append(d.text)
        if len(problems) > 0:
            return problems
        else:
            return []

    def tokenize(self,text):
        if text is None:
            return ['']
        else:
            pass
        if isinstance(text, str) == False:
            logger.warn(F' tokeninizer recieved {type(text)} input')
        else:
            pass
        text_clean = re.sub(r'[^\w]', ' ', str(text)).lower()
        text_clean = replace_history(text_clean)
        text_clean = re.sub('  ', ' ',text_clean).strip()
        tokens = [self.lemmatizer.lemmatize(t) for t in text_clean.split(' ') if len(t)> 1 and t not in self.stop_words]

        logger.debug(F'text input {text} tokenized to {tokens}')
        return tokens

    def get_document_vector(self, text):
        tokens = self.tokenize(text)
        x = []
        logger.debug(F'get document vector input {tokens}')
        for token in tokens:
            v = self.lookup_token(token)
            if isinstance(v, type(None)):
                pass
            else:
                x.append(v)

        logger.debug(F'{tokens} were successfully looked up {len(x)} of {len(tokens)} times')
        try:
            return np.vstack(x).mean(axis=0)
        except ValueError:
            return np.zeros(self.n_dims)

    def lookup_token(self, token:str):
        try:
           x = self.word_vectors[token]
           return x
        except KeyError:
            logger.debug(F'token {token} not found')

    def transform(self, text, min_sim=0.5):
        tokens = self.tokenize(text)
        tokens_joined = ' | '.join(tokens)
        document_vector = np.reshape(self. get_document_vector(tokens_joined), (1, -1))
        distances, indices = self._nbrs.kneighbors(document_vector)
        problems = self.get_problems(' '.join(tokens))
        problem_vec = self.get_document_vector(' '.join(problems)).flatten()
        results = {'text': text,
                   'problems': problems,
                    'tokens': tokens,
                    'code': None,
                    'tags' : None,
                    "code_desc" :None,
                    "cosine_d": None}

        logger.debug(F'looking up {text}, found distance {distances[0]} to index {indices[0]}')
        if document_vector.sum() == 0:
            logger.info(F'text {text} resulted in no word vectors being looked up')
            return results

        desc_vectors = [self.get_document_vector(self._codes.astype(str).iloc[i]) for i in indices.flatten() ]
        cosine_sims = np.array([cosine_similarity(np.reshape(document_vector, (1,-1)), np.reshape(v, (1,-1))) for v in desc_vectors]).flatten()
        best_order = np.argsort(1-cosine_sims)
        results['tags'] = get_condtion_tags(text)
        for i, index in enumerate(indices.flatten()[best_order]):
            code = self._codes.index[index]
            desc = self._codes.iloc[index]
            desc_tags = get_condtion_tags(desc)
            cosine_d = cosine_sims[best_order][i]
            dist_test = cosine_d > min_sim
            problem_dist_test = True
            if len(results['problems']) > 0:
                desc_problems = self.get_problems(desc)
                desc_problem_vect = self.get_document_vector(' '.join(desc_problems)).flatten()
                problem_cosine_sim = cosine_similarity(problem_vec.reshape(1, -1), desc_problem_vect.reshape(1, -1) )
                results['problems_cosine_d'] = problem_cosine_sim[[0]]
                problem_dist_test = all((problem_cosine_sim > min_sim))

            condition_tag_test = all(([d in results['tags'] for d in desc_tags]))
            if condition_tag_test == False:
                logger.info(F'TAGS: : {results["tags"] } desc: {desc_tags}')
            logger.debug(F'detected: {code} |  {desc}  from input {text }')
            if all((dist_test, problem_dist_test)):
                results['code'] = code
                results['code_desc'] = desc
                results['cosine_d'] = cosine_d
                return results
        return results

    def get_nearest_icd9(self, text, min_sim=0.5, return_code=True):
        if return_code:
            return self.transform(text, min_sim=min_sim)['code']
        else:
            return self.transform(text, min_sim=min_sim)['code_desc']
