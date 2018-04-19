import sqlite3 as sqlite
from query_builder import selectQueryBuilder
from settings import *

def GetCastAndCrew(title, year):
    conn = sqlite.connect(DATABASE_NAME)
    cur = conn.cursor()

    sub_query = selectQueryBuilder(
        columns = 'FilmID',
        table = 'Film',
        filter = [['Title', "=", title], "AND", ['Release', 'LIKE', year+'%']]
    )
    query = selectQueryBuilder(
        columns = ['People.ID', 'People.Name', 'Role.Title'],
        table = 'CastByFilm',
        joins = [
            'JOIN People ON CastID = People.ID',
            'JOIN Role ON RoleID = Role.ID'
        ],
        filter = ['FilmID', '=', "("+sub_query+")"],
    )

    cur.execute(query)
    data = []
    for row in cur:
        data.append(row)

    if len(data) > 0:
        return data
    else:
        return None
