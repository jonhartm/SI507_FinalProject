from caching import *
from util import tryParseInt, Timer
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
import sqlite3

Database_Name = 'movies.db'

class FilmAcademyAward():
    def __init__(self):
        self.title = None
        self.year = None
        self.BestPicture = False
        self.Awards = 0
        self.Nominations = 0

    def InsertTuple(self):
        t = [None, self.Awards, self.Nominations, self.title, self.year+'%']
        if (self.BestPicture):
            t[0] = True
        return tuple(t)

    def __str__(self):
        if self.BestPicture:
            return "{} ({}): Best Picture, {} Wins - {} Nominations".format(self.title, self.year, self.Awards, self.Nominations)
        else:
            return "{} ({}): {} Wins - {} Nominations".format(self.title, self.year, self.Awards, self.Nominations)

def AAwardWinningFilms():
    t = Timer()
    t.Start()
    url = 'https://en.wikipedia.org/wiki/List_of_Academy_Award-winning_films'
    AA_Cache = CacheFile('WikipediaCache.json', print_info=True)
    AA_Soup = AA_Cache.CheckCache_Soup(url, strainer=SoupStrainer(class_="wikitable"))
    Films = []
    for row in AA_Soup.find_all("tr"):
        if "Nominations" in row.text:
            pass
        else:
            cols = row.find_all("td")
            f = FilmAcademyAward()
            f.title = cols[0].text
            f.year = cols[1].text.split('/')[0]
            try:
                f.BestPicture = ("#EEDD82" in row.attrs['style'])
            except:
                pass
            f.Awards = tryParseInt(cols[2].text.split(' ')[0])
            f.Nominations = tryParseInt(cols[3].text)
            Films.append(f)

    conn = sqlite3.connect(Database_Name)
    cur = conn.cursor()
    inserts = []
    for film in Films:
        inserts.append(film.InsertTuple())

    statement = '''
        UPDATE Film SET BestPicture=?,AA_Wins=?,AA_Nominations=? WHERE Title == ? AND Release LIKE ?
    '''
    cur.executemany(statement,inserts)

    conn.commit()
    conn.close()
    t.Stop()
    print("Scraping Completed in " + str(t))
