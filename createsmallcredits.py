#-------------------------------------------------------------------------------
# Just a helper that isn't really related to the rest of the program. Credits.csv
# from Kaggle is way to large to do a speedy input (<30secs), so this can create
# a much smaller file based on a SQL query, kind of like what the OMDBAPI load
# does. Creates a list of movie IDs, then iterates through the credits csv and
# creates a smaller version.
#-------------------------------------------------------------------------------

import sqlite3
import pandas as pd
import csv
import os
from settings import *

out_file = "data/small_credits.csv"
os.remove(out_file)
conn = sqlite3.connect("movies.db")
cur = conn.cursor()

statement = 'SELECT FilmID FROM Film WHERE AA_Wins > 1'
# statement = '''
# SELECT FilmID FROM Films
# WHERE Rating_IMDB is not null
# '''
cur.execute(statement)
ids_to_pull = []
for row in cur:
    ids_to_pull.append(row[0])

# with open(out_file, 'w') as f:
#     f.write(','.join(ids_to_pull))

# with open(out_file, 'r') as f:
#     for row in csv.reader(f):
#         for item in row:
#             print(item)
#             input()


chunksize = 100
i = 0
for f in pd.read_csv("data/credits.csv", chunksize=chunksize, iterator=True):
    inserts = []
    for row in f.itertuples():
        movieId = row[3]
        if movieId in ids_to_pull:
            print(str(movieId) + " is in the id list...")
            with open(out_file, 'a', encoding="utf8") as f:
                writer = csv.writer(f)
                writer.writerow([row[1],row[2],str(row[3])])
            i += 1

print(str(i) + " rows added")
