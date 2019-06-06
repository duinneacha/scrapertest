# import urllib.request

import requests
import mysql.connector
from bs4 import BeautifulSoup
from csv import writer

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  database="nimbus-admin"
)



req = requests.get(
    'https://www.rte.ie/feeds/rss/?index=/news/business/')

# soup = BeautifulSoup(response.text, 'xml')

soup = BeautifulSoup(req.text, 'html.parser')

# print(soup)

# for (num, item) in enumerate(soup.contents):
#     print(num+1)
#     print(item)

print("ADDDDD")
print(soup)
print("ADDDDD")


for item in soup.findAll('item'):
   print("AD")
   # print(item)
   print(item.category.get_text())
   print(item.title.get_text())
   print(item.description.get_text())
   print(item.guid.get_text())
   thumb = item.find("media:content")
   print(thumb)
   print(thumb["url"])
   # thumbUrl = thumb.find("url") 
   # print(thumbUrl)



print("mydb:-")
print(mydb)


mycursor = mydb.cursor()

mycursor.execute("SHOW TABLES")

for x in mycursor:
  print(x)


mycursor.execute("SELECT cl_id, cl_name FROM tbl_contacts")

myresult = mycursor.fetchall()

for x in myresult:
  print(x)
