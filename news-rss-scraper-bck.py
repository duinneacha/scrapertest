# import urllib.request

import requests
import mysql.connector
from bs4 import BeautifulSoup
# from csv import writer
from fuzzywuzzy import fuzz, process

import csv
import operator

# print(dir(fuzz))

# Open textfile for raw links to process
with open('linkstempfile.txt', 'w') as link_file:
    pass


contactsQueryData = ''
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="nimbus-admin"
)

mycursor = mydb.cursor()

# RSS Feeds
rssRTEBusNews = 'https://www.rte.ie/feeds/rss/?index=/news/business/'
rssIrishTimes = 'https://www.irishtimes.com/cmlink/news-1.1319192'
rssITBusinessNews = 'https://www.irishtimes.com/rss/activecampaign-business-today-digest-more-from-business-1.3180340'
rssHackerNews = 'https://news.ycombinator.com/rss'
rssGoogleNews = 'https://news.google.com/rss?hl=en-IE&gl=IE&ceid=IE:en'
rssSiliconRepublicNews = 'https://www.siliconrepublic.com/feed'
rssIndependentNews = 'https://www.independent.ie/business/irish/rss/'
rssTheJournalNews = 'https://thejournal.com/rss-feeds/all-articles.aspx'
rssBreakingNewsTop = 'https://feeds.breakingnews.ie/bntopstories'
rssBreakingNewsBusiness = 'https://feeds.breakingnews.ie/bnbusiness'
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


def fetchNewsSites():
    print("In Fetch News Sites!!")
    getNewsStatement = " \
    SELECT news_scraping_sites.use_in_search, news_scraping_sites.site_name, news_scraping_sites.site_address from news_scraping_sites"
    mycursor.execute(getNewsStatement)

    newsSitesQueryData = mycursor.fetchall()
    return newsSitesQueryData


def fetchContactsData():

    getContactsStatement = " \
    SELECT tbl_contacts.cl_name, tbl_contacts.cl_unique_id  \
    FROM tbl_projects \
    LEFT JOIN tbl_contacts \
    on tbl_projects.cl_unique_id = tbl_contacts.cl_unique_id \
    WHERE tbl_projects.pr_status='Project Ongoing' OR tbl_projects.pr_status='Prospect Ongoing' \
    GROUP by tbl_contacts.cl_unique_id"

    mycursor.execute(getContactsStatement)

    contactsQueryData = mycursor.fetchall()
    # print(contactsQueryData)
    # mycursor.close()
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
        # print("In Irish Times News")

        newsTitle = item.title.get_text()

        newsLink = item.find('link').next_element.strip()
        # newsMediaThumbnailLink = item.find("media:thumbnail")["url"]

        try:
            newsMediaThumbnailLink = item.find("enclosure")["url"]
        except:
            newsMediaThumbnailLink = ""

        newsPublishDate = item.pubdate.get_text()

        print("Title: " + newsTitle)
        print("Link:  " + newsLink)
        print("Pic:   " + newsMediaThumbnailLink)
        print("Date:  " + newsPublishDate)
        print("")

        # print(item.prettify())
        # # print(item.category.get_text())
        # print("Title:   " + item.title.get_text())
        # print(item.description.get_text())
        # print(item.guid.get_text())

        # print("link is : " + link)
        # print(thumb["url"])


def printStandardNewsItems(newsObject):
    """ This appears to be a standard format across many rss feed sites"""
    for item in newsObject.findAll('item'):

        newsTitle = item.title.get_text()
        newsLink = item.guid.get_text().strip()
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


def printIndependentNewsItems(newsObject):
    """ Independant.ie business RSS news parser"""
    for item in newsObject.findAll('item'):

        newsTitle = item.title.get_text()
        newsLink = item.find('link').next_element.strip()

        try:
            newsMediaThumbnailLink = item.find("enclosure")["url"]
        except:
            newsMediaThumbnailLink = ""

        # newsMediaThumbnailLink = ""

        typeNewsMediaThumbnailLink = ""
        # if type(item.find("enclosure")["url"]) is str:
        #     print("Is a string")

        newsPublishDate = item.pubdate.get_text()

        print("Title: " + newsTitle)
        print("Link:  " + newsLink)
        # print("Type of Pic:   ")
        # print(typeNewsMediaThumbnailLink)
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

        newsTitle = item.title.get_text()
        newsLink = item.find('link').next_element.strip()

        # print(item.prettify())
        # print(item.category.get_text())
        # print(item.title.get_text())
        # print(item.description.get_text())
        # print(item.guid.get_text())

        link = item.find('link').next_element

        print("Title : " + newsTitle)
        print("link  : " + newsLink)
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

def writeMatchToCSV(fieldList):
    print(fieldList)
    print(fieldList)
    print(fieldList)
    print(fieldList)
    print(fieldList)
    print(fieldList)
    # Open the csv file and check to see if the match is already in the file
    with open('linkstempfile.txt') as read_file:
        reader = csv.reader(read_file)

        count = 0
        t_match = False
        print("In csv read")

        for row in reader:

            if (row[3] == fieldList[3]):
                print("**********************************",
                      row[3], " is a match with ", fieldList[3])
                t_match = True

    if not t_match:
        with open('linkstempfile.txt', 'a+', newline='') as link_file:
            writer = csv.writer(link_file)
            writer.writerow(fieldList)


def parseMatchData(contact, newsItem, matchScore, newsProvider):
    print("In news Item Writing to Database")
    print("News Provider: ", newsProvider)
    print("Fuzz Score:    ", matchScore)
    print("Contact:       ", contact[0])
    print("Contact ID:    ", contact[1])

    newsTitle = newsItem.title.get_text()
    newsPublishDate = newsItem.pubdate.get_text()

    if (newsProvider == "Independent.ie") or (newsProvider == "BreakingNews.ie") or (newsProvider == "TheJournal.ie") or (newsProvider == "Hacker News"):

        newsLink = newsItem.find('link').next_element.strip()

        try:
            newsMediaThumbnailLink = newsItem.find("enclosure")["url"]
        except:
            newsMediaThumbnailLink = ""
    elif (newsProvider == "RTE Business News"):

        newsLink = newsItem.guid.get_text()

        newsMediaThumbnailLink = newsItem.find("media:content")["url"]
    elif (newsProvider == "IT Business") or (newsProvider == "Irish Times"):
        print("IT Match")
        newsLink = newsItem.find('link').next_element.strip()
        try:
            newsMediaThumbnailLink = newsItem.find("enclosure")["url"]
        except:
            newsMediaThumbnailLink = ""
    elif (newsProvider == "Google News"):
        newsMediaThumbnailLink = ""
        newsLink = newsItem.find('link').next_element.strip()
    elif (newsProvider == "Silicon Republic"):
        try:
            newsMediaThumbnailLink = newsItem.find("media:thumbnail")["url"]
        except:
            newsMediaThumbnailLink = ""
        newsLink = newsItem.find('link').next_element.strip()

    print("Title: " + newsTitle)
    print("Link:  " + newsLink)
    print("Pic:   " + newsMediaThumbnailLink)
    print("Date:  " + newsPublishDate)
    print("")

    fieldNames = [newsProvider, contact[0], matchScore, newsTitle, newsLink, newsMediaThumbnailLink, newsPublishDate]

    writeMatchToCSV(fieldNames)



def matchNewsItems(newsProvider, newsList):
    """Take a news list and try to match against the Contacts List """

    for item in newsList.findAll('item'):
        newsHeader = item.title.get_text()

        for contact in contactsQueryData:

            if contact[0] == None:
                continue

            # Field needs to be converted to string from tuple
            contactInLoop = contact[0]

            # map_str = map(str, contact)
            # contactInLoop = ''.join(map_str)

            # fuzzMatch = fuzz.partial_ratio(newsHeader, cleaned(contactInLoop))

            fuzzMatch = fuzz.token_set_ratio(
                newsHeader, cleaned(contactInLoop))

            # In some cases Contact equals None
            # Determine score of relevance
            if fuzzMatch > 70 and cleaned(contactInLoop) != 'None':
                parseMatchData(contact, item, fuzzMatch, newsProvider)


def writeTopNewsItem(newsItem, listNews):
    """Write the top news item is the News Site to the temp file"""
    print("newsItem", newsItem)
    print("listNews", listNews.findAll('item')[0])
    topNewsItem = listNews.findAll('item')[0]
    newsProvider = newsItem[1]
    parseMatchData("Top News", topNewsItem, "Top", newsProvider)
    print(newsItem)

    # input("Press Eeenter . . . .")



# Build the News Lists
contactsQueryData = fetchContactsData()
newsSitesData = fetchNewsSites()
mydb.close()
for index, newsList in enumerate(newsSitesData, start=1):

    print("Index is:", index)

    if newsList[0] == "x":
        print(newsList)

        rssScrapelist = getXMLNews(newsList[2])
        writeTopNewsItem(newsList,rssScrapelist)
        matchNewsItems(newsList[1], rssScrapelist)


rawLinkFile = open('linkstempfile.txt', 'r')
csv1 = csv.reader(rawLinkFile, delimiter=',')
sort = sorted(csv1, key=operator.itemgetter(2))

with open('linkfilesorted.txt', 'w', newline='') as link_sorted:
    writer = csv.writer(link_sorted)
    
    for eachline in sort:
        writer.writerow(eachline)
