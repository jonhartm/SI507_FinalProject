#-------------------------------------------------------------------------------
# INIT_DATABASE.PY
# Functions for Creating/Reseting the SQL database
#-------------------------------------------------------------------------------

import sqlite3 as sqlite
from settings import *
from util import Timer
import time

from load_CSV import Load_CSV
from load_scraping import AAwardWinningFilms
from load_OMDBAPI import InitializeOMDBImport

# reset the database
def ResetDatabase():
    try:
        t = Timer()
        t.Start()
        global cur
        conn = sqlite.connect(DATABASE_NAME)
        cur = conn.cursor()

        ResetTable("Film") # will also reset ratings when it's done
        ResetTable("Credits")

        conn.commit()
        t.Stop()
        print("Database Reset in " + str(t))
    except sqlite.OperationalError as e:
        if str(e) == "database is locked":
            print(DATABASE_NAME + " has pending changes. Write those changes and restart")
        else:
            print("Database ERROR: " + str(e))
            print(type(e))
    except Exception as e:
        print("ERROR: " + str(e))
        print(type(e))

# drops the specified table from the database
def DropTable(table_name):
    statment = 'DROP TABLE IF EXISTS "{}"'.format(table_name)
    cur.execute(statment)

# Reset a table by dropping, recreating, and loading data
def ResetTable(table_name):
    if table_name == "Film":
        DropTable("Film")
        statement = '''
        CREATE TABLE "Film" (
            'FilmID' INTEGER NOT NULL PRIMARY KEY,
            'Title' TEXT,
            'Release' TEXT,
            'Budget' INTEGER,
            'Revenue' INTEGER,
            'Runtime' INTEGER,
            'Rating' TEXT,
            'Poster' TEXT,
            'Rating_IMDB' INTEGER,
            'Rating_RT' INTEGER,
            'Rating_MC' INTEGER,
            'BestPicture' INTEGER,
            'AA_Wins' INTEGER,
            'AA_Nominations' INTEGERS
        );
        '''
        cur.execute(statement)
        Load_CSV(MOVIEMETADATA_CSV)
        DropTable("Film_temp") # drop our temp table
        AAwardWinningFilms()
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
