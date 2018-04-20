#-------------------------------------------------------------------------------
# LOAD_OMDBAPI.PY
# Functions for loading data from the Open Movie Database API
#-------------------------------------------------------------------------------

from caching import *
from secrets import *
from util import Timer
import sqlite3

Database_Name = "movies.db"

# Import from the Open Movie Database
# params: title: the title of the movie
#         year: the year of the file (default=None)
def Import_OMD(title, year=None):
    OMD_Cache = CacheFile('OMDBCache.json')
    url = 'http://www.omdbapi.com'
    params = {'apikey':OMDB_API_KEY, "t":title}
    if year is not None:
        params['y'] = year
    return OMD_Cache.CheckCache_API(url, params, keys = ['Rated', 'Poster', 'Ratings'])

# Does the actual importing from the OMDB and inserts into the database.
# Decides which films to load by running a query to get what are likely
# popular films
def InitializeOMDBImport():
    t = Timer()
    t.Start()
    print("Loading data from OMDB API...")
    conn = sqlite3.connect(Database_Name)
    cur = conn.cursor()
    cur2 = conn.cursor()

    # get ratings for the most popular, most highly rated films, and any film that
    # has won at least 2 academy awards
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
        OR FilmID IN
        	(
        		SELECT FilmID
        		FROM Film
        		WHERE AA_Wins > 1
        	)
    '''
    cur.execute(statement)

    updates = []
    for row in cur:
        try:
            OMD_data = Import_OMD(row[0], row[1][:4])
            values = [None, None, None, None, None, row[0], row[1]]
            values[0] = OMD_data['Rated']
            values[1] = OMD_data['Poster']
            for ratings in OMD_data['Ratings']:
                if ratings['Source'] == "Internet Movie Database": values[2] = ratings['Value'].split('/')[0]
                elif ratings['Source'] == "Rotten Tomatoes": values[3] = ratings['Value']
                if ratings['Source'] == "Metacritic": values[4] = ratings['Value'].split('/')[0]
            updates.append(values)
        except Exception as e:
            pass
    statement = 'UPDATE Film SET Rating=?, Poster=?, Rating_IMDB = ?, Rating_RT=?, Rating_MC=? WHERE Title == ? AND Release == ?';
    cur.executemany(statement, updates)
    conn.commit()
    conn.close()

    t.Stop()
    print("OMDB Import completed in " + str(t))
