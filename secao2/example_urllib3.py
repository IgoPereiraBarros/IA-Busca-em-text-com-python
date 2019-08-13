# -*- coding: utf-8 -*-

"""
Created on Tue Jan 22 20:50:28 2019

@author: developer
"""

import urllib3

http = urllib3.PoolManager()
page = http.request('GET', 'http://www.iaexpert.com.br')
page.status