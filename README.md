# CancerUtils A package for creating features from ICD10 CM, ICD9 a natural text 

## Introduction 
The CancerUtils is an natural language processing system intended to extract concepts useful for understanding 
personal, family histories and comorbidity related to cancer.  Electronic Medical Record Data stores diagnoses and
family history information in a variety of sources including ICD10-CM, ICD9-CM and in unstructured text.  This package
is intended to allow research to extract concepts from all three data sources. This allows a 
comprehensive search of data sources when constructing research projects, that avoids pitfalls of only relying on coded
data. 
## Methods 
This package contains three primary modules, the text, ner, and icd_from_raw_text.  
The text module finds a specific list of conditions, and has a list of utlity functions for finding references in raw text.
The package uses rule sets to determine whether text is referring to screening tests, encounter, family or personal history.

### Methods - Text Module
The text module takes text input and returns a list of associated tags that indicate the context of the phrase
These methods work using rule based regular expressions.  The dictionary condition_tag_dict  contains as set of function names as keys and actual functions as values.  This can be imported with ```from CancerUtils.text import condition_tag_dict```.  These functions return boolean values
and have basic negation detection via spacy (1).  Cancer detection has basic functionality to determine whether a text is referring to screening tests, confirmation of negative test results, or family histories. These methods are designed to work on single sentences or phrases, typically
found in a patients problem list.  To apply to longer text (such as clinical notes), careful sentence level parsing is required. 

The get condition tags method uses all available functions and returns a dictionary attributes detected about given text.
```python
from CancerUtils.text import *
s = "Patient has FH colorectal cancer"
get_condtion_tags(s)
```

#### Core  Text Functions 
+ family_history_of_cancer: text contains reference to a family history of any cancer 
+ family_history_of_breast_cancer:   text contains reference to a family history of breast cancer 
+ first_degree_relative: contains reference to parent, child, or sibling
+ tobacco_user: contains reference to the patient using tobacco
+ crc_cancer: contains a reference the patient having (themselves) colorectal cancer
+ lung_cancer:  contains a reference the patient having (themselves) lung cancer
+ 'increased_risk_for_breast_cancer: text indicates the patient is at increased risk for breast cancer  
+ breast_cancer:  contains a reference the patient having (themselves) breast cancer
+ personal_cancer_history:  text contains reference to a personal history of any cancer 
+ negation: text contains  negating terms
+ pregancy_related: text contains terms relating to pregnancy
+ confirming: text contains confirmatory language
+ encounter: text contains language referring to an encounter with the health system
+ screening: text contains language referring  to a screening test
+ history: text contains language indicating conditions are historical
+ family_reference: text contains a reference to a family or family member 
+ is_inlaw: text contains a reference to an in-law or stepfamily relation  
+ metastatic: text indicates metastatic cancer 
+ advanced_directive: text contains references to advanced directives
+ is_pediactric_related: text contains references to childhood
+ is_cancer: text contains references for cancer 
+ confirmed_neg_for_cancer: text contains language indicating screening is negative for cancer

Example output shows the phrase is flagged as family history, associated with cancer. 
array(['family_history_of_cancer', 'family_reference', 'history',
       'is_cancer'],
More examples of text methods 
```python
s = 'Patient has colorectal cancer'
get_cancer_history_tags(s)
s = 'patient has medicare as primary payer'
get_insurance_tags(s)
```
Example of detecting negation
```python3
  inputs = 'cancer screening test was negative'
  detect_any_negation(inputs)
  ```


### Methods - NER Module 
This module used Named Entity Recognition via Stanza (1,2) to detect clinical problems in text. This package has the capability to 
detect problems, family history and first degree family history (parents, children, siblings). 
The ‘get_problems’ function detects problems attributed to the patient


Available functions:
+ get_problems
+ get_family_history
+ get_first_degree_family_history

example usage 
  ```python3
  from CancerUtils.ner import *
  inputs = 'history of colon cancer in father'
  get_family_history(inputs)
  ```


#### Methods -ICD from Raw Text
This module contains a method to extract ICD9 references from raw unstructured text.  This method uses word vectors, 
and nearest neighbor matching to calculate the distance between a phrase and an ICD9CM description.  
This method transforms text into a document vector using pre-trained word vectors and calculates the ICD9CM with
the closest cosine distance.  A secondary check uses NER to detect a patient problem, and ensures the min cosine distance
is to the problem extracted from the ICD9CM that is closest matched, is met. 
example usage:

```python

from CancerUtils.icd_from_raw_text import TextToIcd9
nn = TextToIcd9().fit()
#  should return ICD9CM '2303'
nn.transform( 'colon cancer')['code']
# should return ICD9CM of 'V170'
nn.get_nearest_icd9('family history of depression') == 'V170'

```


## Installation Instructions
It is recommended to install and run this package in a python virtual enviroment 
install package dependencies
```shel
pip install -r requirments.txt
```

Download spacy and en core web sm to support text functions
```shell
 python -m spacy download en_core_web_sm
```
Download nltk dependency
```python
import nltk
nltk.download('omw-1.4')
```
Install the package from the directory with the setup.py file
```shell
python -m pip install .
```

## Presentations 
1. Utilizing NLP for Structure Learning to Understand Cancer Screening Uptake Utilizing NLP for Structure Learning to Understand Cancer Screening Uptake. NLP Summit. Accessed May 13, 2023. https://www.nlpsummit.org/utilizing-nlp-for-structure-learning-to-understand-cancer-screening-uptake/


## REFERENCES

1. explosion/spaCy: 💫 Industrial-strength Natural Language Processing (NLP) in Python. Accessed July 5, 2023. https://github.com/explosion/spaCy


2. Peng Qi, Yuhao Zhang, Yuhui Zhang, Jason Bolton and Christopher D. Manning. 2020. Stanza: A Python Natural Language Processing Toolkit for Many Human Languages. In Association for Computational Linguistics (ACL) System Demonstrations. 2020. [pdf][bib]


3. Yuhao Zhang, Yuhui Zhang, Peng Qi, Christopher D. Manning, Curtis P. Langlotz. Biomedical and Clinical English Model Packages in the Stanza Python NLP Library, Journal of the American Medical Informatics Association. 2021.



## License


Copyright 2023 Matthew Davis

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
