# import urllib.request

import requests
from bs4 import BeautifulSoup
from csv import writer

req = requests.get(
    'https://www.rte.ie/feeds/rss/?index=/news/business/')

# soup = BeautifulSoup(response.text, 'xml')

soup = BeautifulSoup(req.text, 'html.parser')

# print(soup)

# for (num, item) in enumerate(soup.contents):
#     print(num+1)
#     print(item)


for item in soup.select('.item'):
    print(item.get_text())
