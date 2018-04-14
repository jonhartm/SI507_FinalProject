import sqlite3 as sqlite
from settings import *

DB_Tables = ['Films']

# reset the database.
# if tables is None, resets all of the tables
# if tables is specified, only resets those tables
def ResetDatabase(tables=None):
    global cur
    conn = sqlite.connect(DATABASE_NAME)
    cur = conn.cursor()
    if tables is None:
        tables = DB_Tables

    for t in tables:
        ResetTable(t)

    conn.commit()

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
