# import urllib.request

import requests
import mysql.connector
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz, process
import logging
import csv
import operator




logger = logging.getLogger(__name__)
logging.basicConfig(filename='scrapenews.log', level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:---%(message)s', filemode='w')

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
    
    try:
        req = requests.get(urlLink)
    except Exception as e:
        # print("******************** Error Occurred")
        logger.error('No data received from: {}'.format(e))
        return None
    
    if req.status_code == 200:
        soup = BeautifulSoup(req.text, 'html.parser')
        logger.info('Data Received from: {}'.format(urlLink))
        return soup
    else:
        logger.error('No data received from: {}'.format(urlLink))
        return None


def fetchNewsSites():
    """Fetch the news sites from MYSQL news_scraping_sites table"""

    # input("This is a stop . . .")
    getNewsStatement = " \
    SELECT news_scraping_sites.use_in_search, news_scraping_sites.site_name, news_scraping_sites.site_address from news_scraping_sites"
    mycursor.execute(getNewsStatement)

    newsSitesQueryData = mycursor.fetchall()
    
    logger.info('News Sites fetched from table - news_scraping_sites')
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
    # print(mycursor.rowcount)
    # print(contactsQueryData)
    # mycursor.close()
    logger.info(
        '{} Contacts received from table tbl_contacts'.format(mycursor.rowcount))
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
    """Match found - write this to the csv temporary storing file"""

    # Open the csv file and check to see if the match is already in the file
    with open('linkstempfile.txt') as read_file:
        reader = csv.reader(read_file)

        count = 0
        t_match = False
        # print("In csv read")

        for row in reader:

            if (row[3] == fieldList[3]):
                t_match = True

    if not t_match:
        with open('linkstempfile.txt', 'a+', newline='') as link_file:
            writer = csv.writer(link_file)
            writer.writerow(fieldList)


def parseMatchData(contact, newsItem, matchScore, newsProvider):
    """If match determined - then parse the data from the news item"""

    newsTitle = newsItem.title.get_text()
    if newsProvider == 'The Examiner':
        newsPublishDate = newsItem.published.get_text()
    else:
        newsPublishDate = newsItem.pubdate.get_text()

    # if (newsProvider == "Independent.ie") or (newsProvider == "BreakingNews.ie") or (newsProvider == "TheJournal.ie") or (newsProvider == "Hacker News") or (newsProvider == "Tech Crunch"):
    if newsProvider in ("Independent.ie", "BreakingNews.ie", "TheJournal.ie", "Hacker News", "Tech Crunch"):
        
        newsLink = newsItem.find('link').next_element.strip()

        try:
            newsMediaThumbnailLink = newsItem.find("enclosure")["url"]
        except:
            newsMediaThumbnailLink = ""
    elif (newsProvider == "RTE Business News"):

        newsLink = newsItem.guid.get_text()

        newsMediaThumbnailLink = newsItem.find("media:content")["url"]
    elif newsProvider in ("IT Business", "Irish Times"):
        
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
    elif (newsProvider == "The Examiner"):
        try:
            newsMediaThumbnailLink = newsItem.find("media:thumbnail")["url"]
        except:
            newsMediaThumbnailLink = ""
        newsLink = newsItem.find('link')["href"]

    fieldNames = [newsProvider, contact[0], matchScore, newsTitle,
                  newsLink, newsMediaThumbnailLink, newsPublishDate]

    writeMatchToCSV(fieldNames)


def matchNewsItems(newsProvider, newsList, contactList):
    """Take a news list and try to match against the Contacts List """

    # The Examiner has a differend news tag to the rest of the news sources - entry (not item)
    if newsProvider == "The Examiner":
        headerTag = "entry"
    else:
        headerTag = "item"

    try:
        
        for item in newsList.findAll(headerTag):

            newsHeader = item.title.get_text()
            # print(newsHeader)
            for contact in contactList:

                # In some cases Contact equals None
                if contact[0] == None:
                    continue

                # Field needs to be converted to string from tuple
                contactInLoop = contact[0]

                # fuzzMatch = fuzz.partial_ratio(newsHeader, cleaned(contactInLoop))

                fuzzMatch = fuzz.token_set_ratio(
                    newsHeader, cleaned(contactInLoop))

                # Determine score of relevance
                if fuzzMatch > 70 and cleaned(contactInLoop) != 'None':
                    parseMatchData(contact, item, fuzzMatch, newsProvider)
    except Exception as e:
        # print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%   Error")
        logger.error('No data received from: {}'.format(e))

def writeTopNewsItem(newsItem, listNews):
    """Write the top news item is the News Site to the temp file"""
    newsProvider = newsItem[1]

    try:
        
        # The Examiner is special in that it is the only site that uses "entry" as a news tag
        if newsProvider == "The Examiner":
            topNewsItem = listNews.findAll('entry')[0]
        else:
            topNewsItem = listNews.findAll('item')[0]

        parseMatchData("Top News", topNewsItem, "Top", newsProvider)
        # print(newsItem)

        # input("Press Eeenter . . . .")
    except Exception as e:
        
        logger.error('No data received from: {}'.format(e))


# Build the News Lists

# Get the contacts data from the Contacts database
contactsQueryData = fetchContactsData()

# Get the News Sites from the database
newsSitesData = fetchNewsSites()
mydb.close()

extraList = [("Nimbus", 0), ("CIT", 0), ("Soldo", 0)]

# Loop through the news sites and get Top news item and any news items that are associated with the names in the contacts table
for index, newsList in enumerate(newsSitesData, start=1):

    # print("Index is:", index)

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
