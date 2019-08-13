# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from nltk.stem import RSLPStemmer

engine = create_engine('mysql+pymysql://root:1234@localhost/indice')
conn = engine.connect()


############### MÉTRICAS ###################

def frequency_score(rows):
    score = dict([row[0], 0] for row in rows)
    for row in rows:
        score[row[0]] += 1
    return score

def location_score(rows):
    locations = dict([row[0], 1000000] for row in rows)
    for row in rows:
        sum_ = sum(row[1:])
        if sum_ < locations[row[0]]:
            locations[row[0]] = sum_
    return locations

def distance_score(rows):
    if len(rows[0]) <= 2:
        return dict([(row[0], 1.0) for row in rows])
    distances = dict([(row[0], 1000000) for row in rows])
    for row in rows:
        distance_sum = sum([abs(row[i] - row[i - 1]) for i in range(2, len(row))])
        if distance_sum < distances[row[0]]:
            distances[row[0]] = distance_sum
    return distances


########################################


def search_distance_score(query):
    rows, id_word = search_multi_word(conn, query)
    scores = distance_score(rows)
    #scores = dict([row[0], 0] for row in rows)
    #for row in rows:
        #print(row[0])
    #for url, score in scores.items():
        #print('{} - {}'.format(url, score))
    score_ordered = sorted([(score, url) for (url, score) in scores.items()], reverse=0)
    for (score, idurl) in score_ordered[:10]:
        print('{}\t{}'.format(score, get_url(conn, idurl)))
        
search_distance_score('python programação')


def search_frequency_score(query):
    rows, id_word = search_multi_word(conn, query)
    scores = frequency_score(rows)
    #scores = dict([row[0], 0] for row in rows)
    #for row in rows:
        #print(row[0])
    #for url, score in scores.items():
        #print('{} - {}'.format(url, score))
    score_ordered = sorted([(score, url) for (url, score) in scores.items()], reverse=1)
    for (score, idurl) in score_ordered[:10]:
        print('{}\t{}'.format(score, get_url(conn, idurl)))
        

search_frequency_score('python programação')


def search_location_score(query):
    rows, id_word = search_multi_word(conn, query)
    scores = location_score(rows)
    #scores = dict([row[0], 0] for row in rows)
    #for row in rows:
        #print(row[0])
    #for url, score in scores.items():
        #print('{} - {}'.format(url, score))
    score_ordered = sorted([(score, url) for (url, score) in scores.items()], reverse=0)
    for (score, idurl) in score_ordered[:10]:
        print('{}\t{}'.format(score, get_url(conn, idurl)))
        
search_location_score('python programação')
        

def get_url(conn, idurl):
    result = ''
    cursor = conn.execute('SELECT url FROM urls WHERE idurl = %s', idurl)
    if cursor.rowcount > 0:
        result = cursor.fetchone()[0]
    
    return result
    

def search_multi_word(conn, query):
    list_fields = 'wl1.idurl' # <tabela> word_location wl1
    list_tables = ''
    list_clauses = ''
    words_id = []
    
    words = query.split(' ')
    number_table= 1
    for word in words:
        idword = get_idword(conn, word)
        if idword > 0:
            words_id.append(idword)
            if number_table > 1:
                list_tables += ', '
                list_clauses += ' AND '
                list_clauses += 'wl{}.idurl = wl{}.idurl AND '.format(number_table - 1, number_table)
            list_fields += ', wl{}.location'.format(number_table)
            list_tables += ' word_location wl{}'.format(number_table)
            list_clauses += 'wl{}.idword = {}'.format(number_table, idword)
            number_table += 1
    full_consultation = 'SELECT {} FROM {} WHERE {}'.format(list_fields, list_tables, list_clauses)
    cursor = conn.execute(full_consultation)
    rows = [row for row in cursor]
    list_rows = [tuple(row) for row in rows]
    
    return list_rows, words_id

rows, idwords = search_multi_word(conn, 'python programação')

    
def get_idword(conn, word):
    result = -1
    stemmer = RSLPStemmer()
    cursor = conn.execute('SELECT idword FROM words WHERE word = %s', stemmer.stem(word))
    if cursor.rowcount > 0:
        result = cursor.fetchone()[0]
    return result


#get_idword(conn, 'programação')

def search_one_word(conn, word):
    idword = get_idword(conn, word)
    cursor = conn.execute('SELECT urls.url FROM word_location wl INNER JOIN urls ON wl.idurl = urls.idurl WHERE wl.idword = %s', idword)
    page = set()
    for url in cursor:
        page.add(url[0])
    print('Número de páginas encontradas {}'.format(str(len(page))))
    for url in page:
        print(url)

search_one_word(conn, 'python')