# -*- coding: utf-8 -*-

import urllib3
from bs4 import BeautifulSoup

http = urllib3.PoolManager()
page = http.request('GET', 'https://pt.wikipedia.org/wiki/Linguagem_de_programa%C3%A7%C3%A3o')

soup = BeautifulSoup(page.data, 'lxml')
for tags in soup(['script', 'style']):
    tags.decompose()

content = ' '.join(soup.stripped_strings)