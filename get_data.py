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
        filter = [['Title', "=", title], "AND", ['Release', 'LIKE', str(year)+'%']]
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

class UserReviews():
    def __init__(self, data):
        self.data = data

    def __len__(self):
        return len(self.data)

    def getAvgRating(self):
        i = 0
        total = 0
        for row in self.data:
            i += 1
            total += row[2]
        return round(total/i, 3)

    def getAvgDifference(self):
        i = 0
        total = 0
        for row in self.data:
            i += 1
            total += row[4]
        return round(total/i, 3)


def GetReviewsByUser(id):
    conn = sqlite.connect(DATABASE_NAME)
    cur = conn.cursor()

    query = selectQueryBuilder(
        columns=['Title', 'Release', 'Ratings.Rating', 'ROUND(AvgRating, 2) AS AvgRating', 'ROUND(Ratings.Rating - AvgRating,2) AS Difference'],
        table='Ratings',
        joins = [
            'JOIN Film ON Film.FilmID = Ratings.MovieID',
            'JOIN (SELECT MovieID as AvgMovieID, AVG(Rating) AS AvgRating FROM Ratings GROUP BY MovieID) ON AvgMovieID = Film.FilmID'
        ],
        filter = ['UserID', '=', id],
        order_by = 'Ratings.Rating DESC'
    )

    cur.execute(query)
    data = []
    for row in cur:
        data.append(row)

    if len(data) > 0:
        return UserReviews(data)
    else:
        return None
