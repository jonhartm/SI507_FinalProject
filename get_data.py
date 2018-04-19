import sqlite3 as sqlite
from query_builder import selectQueryBuilder
from settings import *

def GetCastAndCrew(title, year):
    conn = sqlite.connect(DATABASE_NAME)
    cur = conn.cursor()

    sub_query1 = selectQueryBuilder(
        columns = ['CastID As Credit', 'COUNT(*) AS CreditCount'],
        table = 'CastByFilm',
        group_by = 'CastID',
        filter = ['COUNT(*)', ">", 1]
    )

    sub_query2 = selectQueryBuilder(
        columns = 'FilmID',
        table = 'Film',
        filter = [['Title', "=", title], "AND", ['Release', 'LIKE', year+'%']]
    )

    query = selectQueryBuilder(
        columns = ['People.ID', 'People.Name', 'Role.Title', 'CreditCount'],
        table = 'CastByFilm',
        joins = [
            'JOIN People ON CastID = People.ID',
            'JOIN Role ON RoleID = Role.ID',
            'LEFT JOIN ('+sub_query1+') ON Credit = People.ID '
        ],
        filter = ['FilmID', '=', "("+sub_query2+")"],
    )

    cur.execute(query)
    data = []
    for row in cur:
        data.append(row)

    if len(data) > 0:
        return data
    else:
        return None

def GetMoviesByPerson(id):
    conn = sqlite.connect(DATABASE_NAME)
    cur = conn.cursor()

    query = selectQueryBuilder(
        columns=['People.Name', 'Film.Title AS Film', 'Film.Release', 'Role.Title'],
        table='People',
        joins = [
            'JOIN CastByFilm ON CastByFilm.CastID = People.ID',
            'JOIN Role ON CastByFilm.RoleID = Role.ID',
            'JOIN Film ON Film.FilmID = CastByFilm.FilmID'
        ],
        filter = ['People.ID', '=', id]
    )

    cur.execute(query)
    data = []
    for row in cur:
        data.append(row)

    if len(data) > 0:
        return data
    else:
        return None
