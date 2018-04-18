from caching import *
from secrets import *
from util import Timer
import sqlite3

Database_Name = "movies.db"

def Import_OMD(title, year=None):
    OMD_Cache = CacheFile('OMDBCache.json')
    url = 'http://www.omdbapi.com'
    params = {'apikey':OMDB_API_KEY, "t":title}
    if year is not None:
        params['y'] = year
    return OMD_Cache.CheckCache_API(url, params, keys = ['Ratings'])

def InitializeOMDBImport():
    t = Timer()
    t.Start()
    print("Loading data from OMDB API...")
    conn = sqlite3.connect(Database_Name)
    cur = conn.cursor()
    cur2 = conn.cursor()

    # get ratings for the most popular and highly rated films
    statement = '''
    SELECT Title, Release FROM Film
        WHERE FilmID IN
            (
                SELECT MovieID
        		FROM Ratings
        		GROUP BY MovieID
        		HAVING COUNT(*) > 10
        		ORDER BY AVG(Rating)
        		LIMIT 350
            )
        OR FilmID IN
        	(
        		SELECT MovieID
        		FROM Ratings
        		GROUP BY MovieID
        		ORDER BY COUNT(*) DESC
        		LIMIT 500
        	)
    '''
    cur.execute(statement)

    updates = []
    for row in cur:
        try:
            # print("Checking OMDB API for {} ({})".format(row[0],row[1][:4]))
            OMD_data = Import_OMD(row[0], row[1][:4])
            values = [None, None, None, row[0], row[1]]
            for ratings in OMD_data['Ratings']:
                if ratings['Source'] == "Internet Movie Database": values[0] = ratings['Value'].split('/')[0]
                elif ratings['Source'] == "Rotten Tomatoes": values[1] = ratings['Value']
                if ratings['Source'] == "Metacritic": values[2] = ratings['Value'].split('/')[0]
            updates.append(values)
        except Exception as e:
            pass
            # print("unable: " + str(e))
    statement = 'UPDATE Film SET Rating_IMDB = ?, Rating_RT=?, Rating_MC=? WHERE Title == ? AND Release == ?';
    cur.executemany(statement, updates)
    conn.commit()
    conn.close()

    t.Stop()
    print("OMDB Import completed in " + str(t))
