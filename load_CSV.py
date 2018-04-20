import csv
import json
import pandas as pd
import re
import sqlite3
from settings import *
import sys
from util import CleanJSONString, Timer

def Load_CSV(file_to_load):
    global cur, conn
    conn = sqlite3.connect(DATABASE_NAME)
    cur = conn.cursor()
    if file_to_load == MOVIEMETADATA_CSV:
        Load_MovieData()
    elif file_to_load == CREDITS_CSV:
        Load_Credits()
    elif file_to_load == RATINGS_CSV:
        Load_Ratings()
    conn.commit()

def Load_MovieData():
    print("Loading Movie data from CSV...")
    t = Timer()
    t.Start()
    for f in pd.read_csv(MOVIEMETADATA_CSV, iterator=True):
        inserts = []
        for row in f.itertuples():
            inserts.append([
                row[6],
                row[9],
                row[15],
                row[3],
                row[16],
                row[17],
            ])
        statement = 'INSERT INTO Film VALUES (?,?,?,?,?,?,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL)'
    cur.executemany(statement,inserts)

    # the CSV contains duplicate entries for 29 films - remove them here
    statement = '''
        DELETE FROM Film WHERE FilmID IN (SELECT MIN(FilmID) FROM Film GROUP BY FilmID HAVING COUNT(*) > 1)
    '''
    cur.execute(statement)
    t.Stop()
    print("Movie Data loaded in " + str(t))

def Load_Credits():
    print("Loading Film Credits from CSV...")
    t = Timer()
    t.Start()
    chunksize = 30
    i = 0
    sys.stdout.write("loading chunks.")
    for f in pd.read_csv(CREDITS_CSV, chunksize=chunksize, iterator=True):
        inserts = []
        for row in f.itertuples():
            movieId = row[3]
            pattern = r'{.*?}' # pull strings out that are inside brackts
            for cast in re.findall(pattern, row[1]):
                try:
                    cast_json = CleanJSONString(cast)
                    AddPersonToDB(movieId, cast_json['name'], "Cast")
                except Exception as e:
                    with open("errors.txt", 'a', encoding="utf8") as f:
                        f.write("ERR: " + str(e) + "\n")
                        f.write(cast + "\n\n")
                    pass

            for crew in re.findall(pattern, row[2]):
                try:
                    crew_json = CleanJSONString(crew)
                    AddPersonToDB(movieId, crew_json['name'], crew_json['job'])
                except Exception as e:
                    with open("errors.txt", 'a', encoding="utf8") as f:
                        f.write("ERR: " + str(e) + "\n")
                        f.write(crew + "\n\n")
                    pass
        i += 1
        # sys.stdout.write("loading chunk #{} of 25...\n".format(str(i)))
        sys.stdout.write(".")
        sys.stdout.flush()
        # if i == 10:
        #     break
    t.Stop()
    print()
    print("Credits Loaded in " + str(t))

def AddPersonToDB(filmID, Name, Role):
    # check and see if this person has already been added
    cur.execute("SELECT ID FROM People WHERE Name = \"{}\"".format(Name))
    person_id = cur.fetchone()
    if person_id is None:
        statement = "INSERT INTO People (Name) VALUES (?)"
        cur.execute(statement, (Name, ))
        person_id = cur.lastrowid
    else:
        person_id = person_id[0]

    # see if this role has been added. If not, add it. Otherwise, grab it
    cur.execute("SELECT ID FROM Role WHERE Title = \"{}\"".format(Role))
    role_id = cur.fetchone()
    if role_id is None:
        statement = "INSERT INTO Role (Title) VALUES (?)"
        cur.execute(statement, (Role, ))
        role_id = cur.lastrowid
    else:
        role_id = role_id[0]

    # add this person for this movie (assuming these are unique)
    statement = "INSERT INTO CastByFilm VALUES (?,?,?)"
    cur.execute(statement, (filmID, person_id, role_id))

def Load_Ratings():
    print("Loading Ratings data from CSV...")
    t = Timer()
    t.Start()
    chunksize = 100000
    i = 0
    for f in pd.read_csv(RATINGS_CSV, chunksize=chunksize, iterator=True):
        inserts = []
        for row in f.itertuples():
            inserts.append(row[1:])
        statement = 'INSERT INTO Ratings VALUES (?,?,?,?)'
        cur.executemany(statement,inserts)
        conn.commit()
        i += 1
        sys.stdout.write("loading chunk #{}...\n".format(str(i)))
        sys.stdout.flush()
    t.Stop()
    print("Ratings Loaded in "+ str(t))
