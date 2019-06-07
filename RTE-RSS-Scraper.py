# import urllib.request

import requests
import mysql.connector
from bs4 import BeautifulSoup
# from csv import writer
from fuzzywuzzy import fuzz
import csv


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

getContactsStatement = " \
SELECT tbl_contacts.cl_name  \
FROM tbl_projects \
LEFT JOIN tbl_contacts \
on tbl_projects.cl_unique_id = tbl_contacts.cl_unique_id \
WHERE tbl_projects.pr_status='Project Ongoing' OR tbl_projects.pr_status='Prospect Ongoing' \
GROUP by tbl_contacts.cl_unique_id"

# mycursor.execute("SELECT cl_id, cl_name FROM tbl_contacts")
# WHERE tbl_projects.pr_status='Project Ongoing' OR tbl_projects.pr_status='Prospect Ongoing' \
# SELECT tbl_projects.cl_unique_id, tbl_projects.pr_unique_id, tbl_projects.pr_title, tbl_projects.pr_status, tbl_contacts.cl_name  \

mycursor.execute(getContactsStatement)

myresult = mycursor.fetchall()

for x in myresult:
  print(x)


with open('contacts.txt', mode='w') as contacts_file:
    contact_writer = csv.writer(contacts_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for x in myresult:
      print(x)
      contact_writer.writerow(x)
