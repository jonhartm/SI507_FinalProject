import sqlite3 as sqlite
from settings import *
import time

from load_CSV import Load_CSV
from load_scraping import AAForBestPicture
from load_OMDBAPI import InitializeOMDBImport

DB_Tables = ['Films', 'Credits', 'Ratings']

# reset the database.
# if tables is None, resets all of the tables
# if tables is specified, only resets those tables
def ResetDatabase(tables=None):
    start = time.time()
    global cur
    conn = sqlite.connect(DATABASE_NAME)
    cur = conn.cursor()
    if tables is None:
        tables = DB_Tables

    for t in tables:
        ResetTable(t)

    conn.commit()
    end = time.time()
    print("Database Reset in {}ms".format(end-start))

# drops the specified table from the database
def DropTable(table_name):
    statment = 'DROP TABLE IF EXISTS "{}"'.format(table_name)
    cur.execute(statment)

def ResetTable(table_name):
    # bail out if this is not a table I know
    if table_name not in DB_Tables:
        print("unrecognized table: " + table_name)
        return

    if table_name == "Films":
        DropTable("Films")
        statement = '''
        CREATE TABLE "Films" (
            'ID' INTEGER NOT NULL PRIMARY KEY,
            'FilmID' INTEGER,
            'Title' TEXT,
            'Release' TEXT,
            'Budget' INTEGER,
            'Revenue' INTEGER,
            'Runtime' INTEGER,
            'Rating_IMDB' INTEGER,
            'Rating_RT' INTEGER,
            'Rating_MC' INTEGER,
            'AcademyAward' INTEGER
        );
        '''
        cur.execute(statement)
        Load_CSV(MOVIEMETADATA_CSV)
        AAForBestPicture()
        ResetTable("Ratings")
        InitializeOMDBImport()
    elif table_name == "Credits":
        DropTable("CastByFilm")
        statement = '''
            CREATE TABLE "CastByFilm" (
                'FilmID' INTEGER,
                'CastID' INTEGER,
                'RoleID' INTEGER
            )
        '''
        cur.execute(statement)
        DropTable("People")
        statement = '''
            CREATE TABLE "People" (
                'ID' INTEGER NOT NULL PRIMARY KEY,
                'Name' TEXT
            );
        '''
        cur.execute(statement)
        DropTable("Role")
        statement = '''
            CREATE TABLE "Role" (
                'ID' INTEGER NOT NULL PRIMARY KEY,
                'Title' TEXT
            );
        '''
        cur.execute(statement)
        Load_CSV(CREDITS_CSV)
    elif table_name == "Ratings":
        DropTable("Ratings")
        statement = '''
            CREATE TABLE "Ratings" (
                'UserID' INTEGER,
                'MovieID' INTEGER,
                'Rating' INTEGER,
                'Timestamp' INTEGER,
                CONSTRAINT PK_UM PRIMARY KEY (UserID, MovieID)
            );
        '''
        cur.execute(statement)
        Load_CSV(RATINGS_CSV)
