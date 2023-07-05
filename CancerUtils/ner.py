import stanza

import logging
from CancerUtils.setup_logger import logger
from CancerUtils.text import condition_tag_dict

def replace_history(s):
    s = s.lower()\
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


class ProblemExtraction:
    def __init__(self, lang='en', package='craft',processor={'ner': 'i2b2'}):
        try:
            #stanza.download('en', package='mimic', processors={'ner': 'i2b2'})
            self.nlp = stanza.Pipeline(lang , package=package,  processors=processor )
            logger.info(F'Stanza Pipeline loaeded {lang} {package} {processor}')
        except:
            stanza.download(lang , package=package , processors=processor)
            self.nlp = stanza.Pipeline(lang , package=package,  processors=processor )
            logger.info(F'Stanza Pipeline loaeded lan: {lang} package: {package} processors: {processor}')


    def _problem_gen(self, s):
        s_lower = s.lower().replace(',',  ' ').replace('  ', ' ').strip()
        s_lower = replace_history(s_lower)
        doc = self.nlp(s_lower)
        for sentence in doc.sentences:
            problems = [d.text for d in sentence.entities]
            dependencies = [t[0].lemma for t in  sentence.dependencies if t[0].lemma != None]
            lemas = [word.lemma for word in sentence.words if word.lemma != None]
            msg = F'NER Problem Gen \
            \n --inputs: {s}\
            \n --normalized: {s_lower}\
            \n --problems :{problems}\
            \n --lemas :{lemas}\
            \n --dependencies:{dependencies}'
            d = {'problem': ' | '.join(problems), 'sentence': sentence}
            for key, func in condition_tag_dict.items():
                d[key] = func(' '.join([w.text for w in sentence.words]))
            yield d


    def get_problems(self,s, only_conditions=True):
        '''
        uses NER via i2bc clincal model to detect problems in free text
        param: s string natural text
        returns: pipe seperated list of problems


        useage:
            get_problems("H/O colon cancer")

        notes:
            + includes NER for problems
            + basic negation detection
            + family / personal history differtiation
            + screening test  differtiation
            '''
        problem_list = list(self._problem_gen(s))
        if  only_conditions:
            results = [p['problem'] for p in problem_list if all((p['family_reference']==False,
            p['screening']==False, p['encounter']==False,p['negation']==False ))]
        else:
            results = [p['problem'] for p in problem_list]

        if len(results) > 0:
            return ' | '.join(results)
        else:
            return None

