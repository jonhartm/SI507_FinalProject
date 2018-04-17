from caching import *
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
import sqlite3

Database_Name = 'movies.db'

def AAForBestPicture():
    url = 'https://en.wikipedia.org/wiki/Academy_Award_for_Best_Picture'
    AA_Cache = CacheFile('WikipediaCache.json', print_info=True)
    BestPictures = AA_Cache.CheckCache_Soup(url, strainer=SoupStrainer(class_="wikitable"))

    winners = []
    nominees = []

    for decade in BestPictures.find_all(class_="wikitable"):
        # input(decade)
        for table_row in decade.find_all("tr", style={"background:#FAEB86"}):
            row = table_row.find("i")
            if row:
                winners.append(row.text)
        # input(decade)
        for table_row in decade.find_all("tr"):
            row = table_row.find("i")
            if row and row.text not in winners:
                nominees.append(row.text)

    print("Adding Academy Award Winners/Nominees...")
    conn = sqlite3.connect(Database_Name)
    cur = conn.cursor()

    # AA winners are a 1
    for title in winners:
        statement = 'UPDATE Films SET AcademyAward = 1 WHERE Title == "' + title + '"';
        cur.execute(statement)

    # AA nominees are a 0
    for title in nominees:
        statement = 'UPDATE Films SET AcademyAward = 0 WHERE Title == "' + title + '"';
        cur.execute(statement)

    # films without an AA win/nomination are left as null
    conn.commit()
    conn.close()
