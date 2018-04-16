from caching import *
from secrets import *
import sqlite3

Database_Name = "movies.db"

def Import_OMD(title, year=None):
    OMD_Cache = CacheFile('OMDCache.json')
    url = 'http://www.omdbapi.com'
    params = {'apikey':OMDB_API_KEY, "t":title}
    if year is not None:
        params['y'] = year
    return OMD_Cache.CheckCache_API(url, params)

def InitializeOMDBImport():
    print("Loading data from OMDB API...")
    conn = sqlite3.connect(Database_Name)
    cur = conn.cursor()
    cur2 = conn.cursor()

    statement = 'SELECT Title, Release FROM Films WHERE AcademyAward NOT null'
    cur.execute(statement)

    for row in cur:
        try:
            OMD_data = Import_OMD(row[0], row[1][:4])
            statement = 'UPDATE Films SET Rating_IMDB = ?, Rating_RT=?, Rating_MC=? WHERE Title == ?';
            values = [
            OMD_data['Ratings'][0]['Value'].split('/')[0],
            OMD_data['Ratings'][1]['Value'],
            OMD_data['Ratings'][2]['Value'].split('/')[0],
            OMD_data['Title']
            ]
            cur2.execute(statement, values)
            print(values)
        except Exception as e:
            pass
            # print("unable: " + str(e))

    conn.commit()
    conn.close()

# InitializeOMDBImport()
