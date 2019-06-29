# import urllib.request

import requests
import mysql.connector
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz, process

import csv
import operator


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
    """This will fetch the contact data of projects that are open from the contacts table"""

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

    return cleanedItem_H


def writeMatchToCSV(fieldList):

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

    fieldNames = [newsProvider, contact[0], matchScore, newsTitle,
                  newsLink, newsMediaThumbnailLink, newsPublishDate]

    writeMatchToCSV(fieldNames)


def matchNewsItems(newsProvider, newsList, contactList):
    """Take a news list and try to match against the Contacts List """

    for item in newsList.findAll('item'):
        newsHeader = item.title.get_text()

        for contact in contactList:

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
    # print("newsItem", newsItem)
    # print("listNews", listNews.findAll('item')[0])
    topNewsItem = listNews.findAll('item')[0]
    newsProvider = newsItem[1]
    parseMatchData("Top News", topNewsItem, "Top", newsProvider)
    # print(newsItem)

    # input("Press Eeenter . . . .")


# Build the News Lists
contactsQueryData = fetchContactsData()
newsSitesData = fetchNewsSites()
mydb.close()

extraList = [("Nimbus", 0), ("Funding", 0), ("Sex Pot", 0)]


for index, newsList in enumerate(newsSitesData, start=1):

    print("Index is:", index)

    if newsList[0] == "x":
        print(newsList)

        rssScrapelist = getXMLNews(newsList[2])
        writeTopNewsItem(newsList, rssScrapelist)
        matchNewsItems(newsList[1], rssScrapelist, contactsQueryData)
        matchNewsItems(newsList[1], rssScrapelist, extraList)


rawLinkFile = open('linkstempfile.txt', 'r')
csv1 = csv.reader(rawLinkFile, delimiter=',')
sort = sorted(csv1, key=operator.itemgetter(2))

with open('linkfilesorted.txt', 'w', newline='') as link_sorted:
    writer = csv.writer(link_sorted)

    for eachline in sort:
        writer.writerow(eachline)


def printExaminerNewsItems(newsObject):
    """ Independant.ie business RSS news parser"""
    print("Down south the Cork Examiner is the one they call the Paper")
    print("Down south the Cork Examiner is the one they call the Paper")
    print("Down south the Cork Examiner is the one they call the Paper")
    print("Down south the Cork Examiner is the one they call the Paper")
    print("Down south the Cork Examiner is the one they call the Paper")
    print("Down south the Cork Examiner is the one they call the Paper")
    print("Down south the Cork Examiner is the one they call the Paper")
    print("Down south the Cork Examiner is the one they call the Paper")
    print("Down south the Cork Examiner is the one they call the Paper")
    print("Down south the Cork Examiner is the one they call the Paper")
    print("Down south the Cork Examiner is the one they call the Paper")

    for item in newsObject.findAll('entry'):
        print(item)
        newsTitle = item.title.get_text()
        newsLink = item.find('link').next_element.strip()
        adNewsLink = item.find('link')["href"]

        try:
            newsMediaThumbnailLink = item.find("enclosure")["url"]
        except:
            newsMediaThumbnailLink = ""

        # newsMediaThumbnailLink = ""

        typeNewsMediaThumbnailLink = ""
        # if type(item.find("enclosure")["url"]) is str:
        #     print("Is a string")

        newsPublishDate = item.published.get_text()

        print("Title: " + newsTitle)
        print("Link:  " + newsLink)
        print("ADLink:", adNewsLink)
        # print("Type of Pic:   ")
        # print(typeNewsMediaThumbnailLink)
        print("Pic:   " + newsMediaThumbnailLink)
        print("Date:  " + newsPublishDate)
        print("")


rssExaminer = getXMLNews('https://feeds.feedburner.com/iebusiness')
printExaminerNewsItems(rssExaminer)
