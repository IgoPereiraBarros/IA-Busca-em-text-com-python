# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
http = urllib3.PoolManager()
page = http.request('GET', 'https://pt.wikipedia.org/wiki/Linguagem_de_programa%C3%A7%C3%A3o')

page.status

soup = BeautifulSoup(page.data, 'lxml')
soup

soup.title
soup.title.string

links = soup.find_all('a')
len(links)

for link in links:
    print(link.get('href'))
    print(link.contents)