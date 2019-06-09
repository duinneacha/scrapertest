# import urllib.request

import requests
import mysql.connector
from bs4 import BeautifulSoup
# from csv import writer
from fuzzywuzzy import fuzz, process
import csv


mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="nimbus-admin"
)

rssRTEBusinessNews = 'https://www.rte.ie/feeds/rss/?index=/news/business/'

rssIrishTimes = 'https://www.irishtimes.com/cmlink/news-1.1319192'

# print(rssRTEBusinessNews)


def getRTENews(rssRTE):
    req = requests.get(rssRTE)
    if req.status_code == 200:
        print("Success!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        soup = BeautifulSoup(req.text, 'html.parser')
        return soup
    elif req.status_code == 404:
        print("URL Not Found!")
        return None
    else:
        print("A Problem occurred")
        return None


def getIrishTimesNews(rssIrishTimes):
    req = requests.get(rssIrishTimes)
    if req.status_code == 200:
        print("Success!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        soup = BeautifulSoup(req.text, 'html.parser')
        return soup
    elif req.status_code == 404:
        print("URL Not Found!")
        return None
    else:
        print("A Problem occurred")
        return None


def fetchContactsData():
    mycursor = mydb.cursor()

    getContactsStatement = " \
    SELECT tbl_contacts.cl_name  \
    FROM tbl_projects \
    LEFT JOIN tbl_contacts \
    on tbl_projects.cl_unique_id = tbl_contacts.cl_unique_id \
    WHERE tbl_projects.pr_status='Project Ongoing' OR tbl_projects.pr_status='Prospect Ongoing' \
    GROUP by tbl_contacts.cl_unique_id"

    mycursor.execute(getContactsStatement)

    contactsQueryData = mycursor.fetchall()
    return contactsQueryData


listRTE = getRTENews(rssRTEBusinessNews)
listIrishTimes = getIrishTimesNews(rssIrishTimes)

if listRTE == None:
    print("Nothing returned in RTE!!")

# soup = BeautifulSoup(response.text, 'xml')


contactsQueryData = fetchContactsData()


# print(soup)

# for (num, item) in enumerate(soup.contents):
#     print(num+1)
#     print(item)

# print("ADDDDD")
# print(soup)
# print("ADDDDD")


# for item in listRTE.findAll('item'):
#     print("AD")
#     # print(item)
#     print(item.category.get_text())
#     print(item.title.get_text())
#     print(item.description.get_text())
#     print(item.guid.get_text())
#     thumb = item.find("media:content")
#     print(thumb)
#     print(thumb["url"])

# print("mydb:-")
# print(mydb)


# mycursor = mydb.cursor()

# mycursor.execute("SHOW TABLES")
# print(mycursor)

# for x in mycursor:
# print("")


# for x in myresult:
#     print(x)


# with open('contacts.txt', mode='w') as contacts_file:
#     contact_writer = csv.writer(
#         contacts_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
#     for x in contactsQueryData:
#         print(x)
#         contact_writer.writerow(x)


for item in listRTE.findAll('item'):
    # print("AD")
    # print(item)
    # print(item.title.get_text())
    newsHeader = item.title.get_text()
    for contact in contactsQueryData:
        # print(item.title.get_text())
        # print(contact)
        fuzzMatch = fuzz.partial_ratio(newsHeader, contact)
        # fuzzMatch = fuzz.WRatio(contact, newsHeader)
        # fuzzMatch = fuzz.token_sort_ratio(contact, newsHeader)
        if fuzzMatch > 50:
            print(fuzzMatch)
            print(newsHeader)
            print(contact)

print("**************************************")
print("**************************************")
print("**************************************")
print("**************************************")
print("**************************************")
print("**************************************")

for item in listIrishTimes.findAll('item'):
    newsHeader = item.title.get_text()
    for contact in contactsQueryData:
        # print(item.title.get_text())
        # print(contact)
        fuzzMatch = fuzz.partial_ratio(newsHeader, contact)
        # fuzzMatch = fuzz.WRatio(contact, newsHeader)
        # fuzzMatch = fuzz.token_sort_ratio(contact, newsHeader)
        if fuzzMatch > 50:
            print(fuzzMatch)
            print(newsHeader)
            print(contact)
