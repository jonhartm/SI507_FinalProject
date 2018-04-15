import csv
import json
import pandas as pd
import re
import sqlite3
from settings import *
import sys
from util import CleanJSONString

def Load_CSV(file_to_load):
    global cur
    conn = sqlite3.connect(DATABASE_NAME)
    cur = conn.cursor()
    if file_to_load == MOVIEMETADATA_CSV:
        Load_MovieData()
    elif file_to_load == CREDITS_CSV:
        Load_Credits()
    conn.commit()

def Load_MovieData():
    print("Loading Movie data from CSV...")
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
        statement = 'INSERT INTO Films VALUES (NULL,?,?,?,?,?,?,NULL,NULL,NULL,NULL)'
    cur.executemany(statement,inserts)

    # the CSV contains duplicate entries for 29 films - remove them here
    statement = '''
        DELETE FROM Films WHERE ID IN (SELECT MIN(ID) FROM Films GROUP BY FilmId HAVING COUNT(*) > 1)
    '''
    cur.execute(statement)

def Load_Credits():
    print("Loading Film Credits from CSV...")
    with open(CREDITS_CSV) as credits_csv:
        data = csv.reader(credits_csv)
        # next(data, None) #skip the headers
        for row in data:
            movieId = row[2]
            pattern = r'{.*?}' # pull strings out that are inside brackts
            for cast in re.findall(pattern, row[0]):
                try:
                    cast_json = json.loads(CleanJSONString(cast))
                    AddPersonToDB(movieId, cast_json['name'], "Cast")
                except Exception as e:
                    print(cast)
                    print("ERR: " + str(e))
                    pass

            for crew in re.findall(pattern, row[1]):
                try:
                    crew_json = json.loads(CleanJSONString(crew))
                    AddPersonToDB(movieId, crew_json['name'], crew_json['job'])
                except Exception as e:
                    print(crew)
                    print("ERR: " + str(e))
                    pass

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
