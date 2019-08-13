# -*- coding: utf-8 -*-

import re
import urllib3
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from sqlalchemy import create_engine

from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer

engine = create_engine('mysql+pymysql://root:1234@localhost/indice1?charset=utf8mb4', encoding='utf-8', pool_recycle=1)
conn = engine.connect()


def get_idurl_relationship(conn, idurl_origin, idurl_destination):
    idurl_relationship = -1
    cursor = conn.execute('SELECT idurl_relationship FROM url_relationship WHERE idurl_origin = %s AND idurl_destination = %s', (idurl_origin, idurl_relationship))
    if cursor.rowcount > 0:
        idurl_relationship = cursor.fetchone()[0]
    return idurl_relationship

get_idurl_relationship(conn, 21, 21)


def get_idurl(conn, url):
    idurl = -1
    cursor = conn.execute('SELECT idurl FROM urls WHERE url = %s', url)
    if cursor.rowcount > 0:
        idurl = cursor.fetchone()[0]
    return idurl

get_idurl(conn, 'www.google.com')

def insert_url_relationship(conn, idurl_origin, idurl_destination):
    cursor = conn.execute('INSERT INTO url_relationship (idurl_origin, idurl_destination) VALUES (%s, %s)', (idurl_origin, idurl_destination))
    idurl_relationship = cursor.lastrowid
    return idurl_relationship

#insert_url_relationship(conn, 3, 4)
    
def insert_url_word(conn, id_word, idurl_relationship):
    cursor = conn.execute('INSERT INTO url_word (idword, idurl_relationship) VALUES (%s, %s)', (id_word, idurl_relationship))
    idurl_word = cursor.lastrowid
    return idurl_word

insert_url_word(conn, 45313, 1)

def insert_wordlocation(conn, idurl, idword, location):
    cursor = conn.execute('INSERT INTO word_location (idurl, idword, location) VALUES (%s, %s, %s)', (idurl, idword, location))
    idwordlocation = cursor.lastrowid
    return idwordlocation


def insert_word(conn, word):
    cursor = conn.execute('INSERT INTO words (word) VALUES (%s)', word)
    idword = cursor.lastrowid
    return idword


def indexed_word(conn, word):
    result = -1 # não existe a palavra no indice
    cursor = conn.execute('SELECT idword FROM words WHERE word = %s', word)
    if cursor.rowcount > 0:
        print('Palavra existe')
        result = cursor.fetchone()[0] # retorna o id da palavra, caso a palavra já esteja na base de dados
    else:
        print('Palavra não existe')
    
    return result

indexed_word(conn, 'python')
    


def insert_page(conn, url):
    cursor = conn.execute('INSERT INTO urls (url) VALUES (%s)', url)
    idpage = cursor.lastrowid
    return idpage


def indexed_page(conn, url):
    result = -1 # não existe a página
    cursor_url = conn.execute('SELECT idurl FROM urls WHERE url = %s', url)
    if cursor_url.rowcount > 0:
        #print('URL cadastrada')
        idurl = cursor_url.fetchone()[0]
        cursor_word = conn.execute('SELECT idurl FROM word_location WHERE idurl = %s', idurl)
        if cursor_word.rowcount > 0:
            #print('Url com palavra')
            result = -2  # Existe página com palavras cadastradas
        else:
            #print('Url sem palavra')
            result = idurl # Existe a página sem palavras, então retorna o id da página
    #else:
        #print('Url nao cadastrada')
    
    return result
    


def separates_words(text):
    stop_words = stopwords.words('portuguese')
    stemmer = RSLPStemmer()
    splitter = re.compile('\W+')
    list_words = []
    words = [p for p in splitter.split(text) if p != '']
    for word in words:
        if word.lower() not in stop_words:
            if len(word) > 1:
                list_words.append(stemmer.stem(word).lower())
    return list_words
    

def get_text(soup):
    for remove_tags in soup(['script', 'style']):
        remove_tags.decompose()
    return ' '.join(soup.stripped_strings)


def indexer(url, soup):
    indexed = indexed_page(conn, url)
    if indexed == -2:
        print('Url já cadastrada')
        return
    elif indexed == -1:
        idurl = insert_page(conn, url)
    elif indexed > 0:
        idurl = indexed
    
    print('Indexado ' + url)
    
    text = get_text(soup)
    words = separates_words(text)
    for i in range(len(words)):
        word = words[i]
        idword = indexed_word(conn, word)
        if idword == -1:
            idword = insert_word(conn, word)
        insert_wordlocation(conn, idurl, idword, i)

def crawl(pages, depth):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    for i in range(depth):
        new_pages = set()
        for page in pages:
            http = urllib3.PoolManager()
            try:
                data_page = http.request('GET', page)
            except:
                print('Erro ao acessar a página ' + page)
                continue
            
            soup = BeautifulSoup(data_page.data, 'lxml')
            indexer(page, soup)
            links = soup.find_all('a')
            count = 1
            for link in links:
                #print(str(link.contents) + ' - ' + str(link.get('href')))
                #print(link.attrs)
                #print('\n')
                if 'href' in link.attrs:
                    url = urljoin(page, str(link.get('href')))
                    #if url != link.get('href'):
                        #print(url)
                        #print(link.get('href'))
                        
                    if url.find("'") != -1:
                        continue
                    
                    #print(url)
                    url = url.split('#')[0]
                    #print(url)
                    #print('\n')
                    if url[:4] == 'http':
                        new_pages.add(url)
                    count += 1
            pages = new_pages
        #print(count)

# 1 -> 396 -> 20.000 -> 1.000.000
list_pages = ['https://pt.wikipedia.org/wiki/Linguagem_de_programa%C3%A7%C3%A3o']
crawl(list_pages, 2)

