
import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="nimbus-admin"
)


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
rssExaminerNews = 'https://feeds.feedburner.com/iebusiness'
rssTechCrunch = 'http://feeds.feedburner.com/TechCrunch/'


def checkTableExists(dbcon, tablename):
    dbcur = dbcon.cursor()
    dbcur.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name = '{0}'
        """.format(tablename.replace('\'', '\'\'')))
    if dbcur.fetchone()[0] == 1:
        dbcur.close()
        return True

    dbcur.close()
    return False


mycursor = mydb.cursor()
dbTable = "news_scraping_sites"
t_Exist = checkTableExists(mydb, dbTable)
if t_Exist:
    print(dbTable, "Already exists - Dropping")
    mycursor.execute("DROP TABLE news_scraping_sites")

mycursor.execute(
    "CREATE TABLE news_scraping_sites (use_in_search VARCHAR(1), site_name VARCHAR(100), site_address VARCHAR(150))")


# if (newsProvider == "Independent.ie") or (newsProvider == "BreakingNews.ie") or (newsProvider == "TheJournal.ie"):

sql = "INSERT INTO news_scraping_sites(use_in_search, site_name, site_address) VALUES (%s, %s, %s)"


valRTE = ("x", "RTE Business News", rssRTEBusNews)
valInd = ("x", "Independent.ie", rssIndependentNews)
valIT = ("x", "Irish Times", rssIrishTimes)
valITB = ("x", "IT Business", rssITBusinessNews)
valBN = ("x", "BreakingNews.ie", rssBreakingNewsBusiness)
valTJ = ("x", "TheJournal.ie", rssTheJournalNews)
valGN = ("x", "Google News", rssGoogleNews)
valSR = ("x", "Silicon Republic", rssSiliconRepublicNews)
valHN = ("x", "Hacker News", rssHackerNews)
valTE = ("x", "The Examiner", rssExaminerNews)
valTC = ('x', "Tech Crunch", rssTechCrunch)

mycursor.execute(sql, valRTE)
mycursor.execute(sql, valIT)
mycursor.execute(sql, valITB)
mycursor.execute(sql, valInd)
mycursor.execute(sql, valBN)
mycursor.execute(sql, valTJ)
mycursor.execute(sql, valSR)
mycursor.execute(sql, valHN)
mycursor.execute(sql, valGN)
mycursor.execute(sql, valTE)
mycursor.execute(sql, valTC)
print("Adding News Sites")


mydb.commit()
mydb.close()
