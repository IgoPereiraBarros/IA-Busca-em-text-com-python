# -*- coding: utf-8 -*-

import re
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer

stopwords = stopwords.words('portuguese')
#stopwords.append('é')
stemmer = RSLPStemmer()

regx = re.compile('\W+')

list_word = []
list_ = [p for p in regx.split('Este lugar é apavorante a c c++') if p != '']

for p in list_:
    if p.lower() not in stopwords:
        if len(p) > 1:
            list_word.append(stemmer.stem(p).lower())
