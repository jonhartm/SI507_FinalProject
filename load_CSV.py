import csv
import json
import pandas as pd
import sqlite3
from settings import *
import sys

def Load_CSV(file_to_load):
    if file_to_load == MOVIEMETADATA_CSV:
        Load_MovieData()

def Load_MovieData():
    conn = sqlite3.connect(DATABASE_NAME)
    cur = conn.cursor()
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
    conn.commit()

    # the CSV contains duplicate entries for 29 films - remove them here
    statement = '''
        DELETE FROM Films WHERE ID IN (SELECT MIN(ID) FROM Films GROUP BY FilmId HAVING COUNT(*) > 1)
    '''
    cur.execute(statement)
