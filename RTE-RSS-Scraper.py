# import urllib.request

import requests
import mysql.connector
from bs4 import BeautifulSoup
# from csv import writer
from fuzzywuzzy import fuzz, process

import csv

# print(dir(fuzz))


contactsQueryData = ''
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="nimbus-admin"
)


# RSS Feeds
rssRTEBusNews = 'https://www.rte.ie/feeds/rss/?index=/news/business/'
rssIrishTimes = 'https://www.irishtimes.com/cmlink/news-1.1319192'
rssITBusinessNews = 'https://www.irishtimes.com/rss/activecampaign-business-today-digest-more-from-business-1.3180340'
rssHackerNews = 'https://news.ycombinator.com/rss'
rssGoogleNews = 'https://news.google.com/rss?hl=en-IE&gl=IE&ceid=IE:en'
rssSiliconRepublicNews = 'https://www.siliconrepublic.com/feed'
webITBusinessNews = 'https://www.irishtimes.com/business/companies'

# This will return a BeautifulSoup object from a specified RSS news feed URL


def getXMLNews(urlLink):
    """ In getXMS News - this takes the url link and returns the page as an object """
    
    req = requests.get(urlLink)
    if req.status_code == 200:
        print("Success!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        soup = BeautifulSoup(req.text, 'html.parser')
        return soup
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


def printNewsItems(newsObject):
    for item in newsObject.findAll('item'):
        # print("In RTE News")
        # print(item)
        # print(item.category.get_text())
        print(" - " + item.title.get_text())
        # print(item.description.get_text())
        # print(item.guid.get_text())
        thumb = item.find("media:content")
        # print(thumb)
        # print(thumb["url"])


def printITNewsItems(newsObject):
    for item in newsObject.findAll('item'):
        print("In Irish Times News")
        print(item.prettify())
        # print(item.category.get_text())
        print(item.title.get_text())
        print(item.description.get_text())
        print(item.guid.get_text())

        link = item.find('link').next_element

        print("link is : " + link)
        # print(thumb["url"])

def printStandardNewsItems(newsObject):
    """ This appears to be a standard format across many rss feed sites"""
    for item in newsObject.findAll('item'):

        newsTitle = item.title.get_text()
        newsLink = item.guid.get_text()
        newsMediaThumbnailLink = item.find("media:thumbnail")["url"]
        newsPublishDate = item.pubdate.get_text()
        

        print("Title: " + newsTitle)
        print("Link:  " + newsLink)
        print("Pic:   " + newsMediaThumbnailLink)
        print("Date:  " + newsPublishDate)
        print("")



        # link = item.find('link').next_element

        # print("link is : " + link)
        # print(thumb["url"])
 

def get_matches(query, choices, limit=3):
    results = process.extract(query, choices, limit=limit)
    return results


def printGoogleNewsItems(newsObject):
    """Parse the information from the Google News Object"""

    for item in newsObject.findAll('item'):
        print("In Google News")
        print(item.prettify())
        # print(item.category.get_text())
        print(item.title.get_text())
        print(item.description.get_text())
        print(item.guid.get_text())

        link = item.find('link').next_element

        print("link is : " + link)
        # print(thumb["url"])


def cleaned(currentContact):
    """Clean the Contact of common words to increase the acuracy of the fuzzy search"""

    cleanedItem_A = currentContact.replace('Ireland', '')
    cleanedItem_B = cleanedItem_A.replace('Limited', '')
    cleanedItem_C = cleanedItem_B.replace('LIMITED', '')
    cleanedItem_D = cleanedItem_C.replace('Ltd', '')
    cleanedItem_E = cleanedItem_D.replace('Ltd.', '')
    cleanedItem_F = cleanedItem_E.replace('limited', '')
    cleanedItem_G = cleanedItem_F.replace('ltd', '')
    cleanedItem_H = cleanedItem_G.replace('Irish', '')

    # for r in (("Limited", ""), ("LIMITED", ""), ("ltd", ""),("Ltd.",""), ("Ltd","")):
    #     cleanedItem = newsHeader.replace(*r)

#     cleanedItem = newsHeader.replace('Ltd', '')
#     cleanedItem = newsHeader.replace('ltd', '')

    # print("Cleaning . . . .")
    # print("Contact Name:   ", newsHeader)
    # print("Cleaned Name:   ", cleanedItem_G)

    return cleanedItem_H


def matchNewsItems(newsList):
    """Take a news list and try to match against the Contacts List """

    for item in newsList.findAll('item'):
        newsHeader = item.title.get_text()

        for contact in contactsQueryData:

            # Field needs to be converted to string from tuple
            contactInLoop = ''

            map_str = map(str, contact)

            contactInLoop = ''.join(map_str)

            # fuzzMatch = fuzz.partial_ratio(newsHeader, cleaned(contactInLoop))

            fuzzMatch = fuzz.token_set_ratio(
                newsHeader, cleaned(contactInLoop))

            # In some cases Contact equals None
            # Determine score of relevance
            if fuzzMatch > 70 and cleaned(contactInLoop) != 'None':
                print(newsHeader)
                print(cleaned(contactInLoop))
                print("The score of fuzzywuzzy is " + str(fuzzMatch))





# def main_function():
""" Build Lists, Parse Lists, Get Contacts, Match Contacts """

# Build the News Lists
# listRTE = getXMLNews(rssRTEBusNews)
# listIrishTimes = getXMLNews(rssIrishTimes)


# listGoogleNews = getXMLNews(rssGoogleNews)
listSiliconRepublic = getXMLNews(rssSiliconRepublicNews)

# Parse the News Lists
# printNewsItems(listRTE)
# printITNewsItems(listIrishTimes)
# printGoogleNewsItems(listGoogleNews)
printStandardNewsItems(listSiliconRepublic)

# if listRTE == None:
    # print("Nothing returned in RTE!!")

# Fetch the information from the Nimbus Contacts SQL Table
contactsQueryData = fetchContactsData()


# Match the news items against the contacts table 
# matchNewsItems(listRTE)
# matchNewsItems(listIrishTimes)
# matchNewsItems(listGoogleNews)



# listwebITBusiness = getXMLNews(webITBusinessNews)
# print(listwebITBusiness)

# main_function()


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


# for item in listRTE.findAll('item'):
#     # print("AD")
#     # print(item)
#     # print(item.title.get_text())
#     newsHeader = item.title.get_text()
#     for contact in contactsQueryData:
#         # print(item.title.get_text())
#         # print(contact)
#         fuzzMatch = fuzz.partial_ratio(newsHeader, contact)
#         # fuzzMatch = fuzz.WRatio(contact, newsHeader)
#         # fuzzMatch = fuzz.token_sort_ratio(contact, newsHeader)
#         if fuzzMatch > 50:
#             print(fuzzMatch)
#             print(newsHeader)
#             print(contact)

# print("**************************************")
# print("**************************************")
# print("**************************************")
# print("**************************************")
# print("**************************************")
# print("**************************************")

# for item in listIrishTimes.findAll('item'):
#     newsHeader = item.title.get_text()
#     for contact in contactsQueryData:
#         # print(item.title.get_text())
#         # print(contact)
#         fuzzMatch = fuzz.partial_ratio(newsHeader, contact)
#         # fuzzMatch = fuzz.WRatio(contact, newsHeader)
#         # fuzzMatch = fuzz.token_sort_ratio(contact, newsHeader)
#         if fuzzMatch > 50:
#             print(fuzzMatch)
#             print(newsHeader)
#             print(contact)
