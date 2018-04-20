#-------------------------------------------------------------------------------
# GET_DATA.PY
# Gets data for displaying in tables that isn't nessecarily associated with a
# specific plotly graph from CREATE_PLOTLY.PY
#-------------------------------------------------------------------------------

import sqlite3 as sqlite
from query_builder import selectQueryBuilder
from load_OMDBAPI import ImportAndAddOMDBData
from settings import *

# Gets a list of the cast and crew for a film
# params: title: the title of the Film
#         year: the year the film was released
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

# Gets a list of the films a person is related to in the database
# params: id: the Id of this person in the People table
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

# Class for Loading basic details about a movie
class MovieDetails():
    # params: title: the title of the Film
    #         year: the year the film was released
    def __init__(self, title, year):
        conn = sqlite.connect(DATABASE_NAME)
        cur = conn.cursor()
        query = 'SELECT * FROM Film WHERE Title="{}" AND Release LIKE "{}%"'.format(title, year)
        cur.execute(query)
        data = cur.fetchone()

        self.id = data[0]
        self.title = data[1]
        self.release = data[2]
        self.budget = data[3]
        self.revenue = data[4]
        self.runtime = data[5]
        self.rating = data[6]
        self.poster = data[7]

        # If data from the OMDB API is missing for this movie, see if we can grab it real quick
        if self.rating is None and self.poster is None:
            data = ImportAndAddOMDBData(title, year)
            self.rating = data['Rated']
            self.poster = data['Poster']

        query = 'SELECT COUNT(*) FROM Ratings WHERE MovieID = {}'.format(self.id)
        cur.execute(query)
        data = cur.fetchone()
        self.total_reviews = data[0]

    # gets a currency formatted string to display the film's budget
    def getBudget(self):
        return '${:,.2f}'.format(self.budget)

    # gets a currency formatted string to display the film's revenue
    def getRevenue(self):
        return '${:,.2f}'.format(self.revenue)

    # gets a currency formatted string to display the film's profit
    # will return None if either Budget or Revenue was not supplied
    def getProfit(self):
        if self.revenue == 0 or self.budget == 0:
            return None
        return '${:,.2f}'.format(self.revenue - self.budget)

# class for loading and sorting User Review data for the User table
class UserReviews():
    def __init__(self, data):
        self.data = data

    # Gets the number of reviews in this set
    def __len__(self):
        return len(self.data)

    # Returns a sorted copy of the data
    # params: sort: The Column to sort by. either "UserRating", "AvgUserRating", or "Difference"
    #         order: Should the column be sorted in ascending or descending order
    def getData(self, sort="UserRating", order="desc"):
        if sort == "UserRating":
            return sorted(self.data, key=lambda x: x[2], reverse=(order=="desc"))
        elif sort == "AvgUserRating":
            return sorted(self.data, key=lambda x: x[3], reverse=(order=="desc"))
        elif sort == "Difference":
            return sorted(self.data, key=lambda x: x[4], reverse=(order=="desc"))
        else:
            raise ValueError("Unknown Sort type in UserReviews.GetData(): " + sort)

    # gets the average rating this user gave across all reviews
    def getAvgRating(self):
        i = 0
        total = 0
        for row in self.data:
            i += 1
            total += row[2]
        return round(total/i, 3)

    # gets the average difference between this user's reviews and all other reviews
    def getAvgDifference(self):
        i = 0
        total = 0
        for row in self.data:
            i += 1
            total += row[4]
        return round(total/i, 3)

# Gets a list of the reviews submitted by this user
def GetReviewsByUser(id):
    conn = sqlite.connect(DATABASE_NAME)
    cur = conn.cursor()

    query = selectQueryBuilder(
        columns=['Title', 'Release', 'Ratings.Rating', 'ROUND(AvgRating, 2) AS AvgRating', 'ROUND(Ratings.Rating - AvgRating,2) AS Difference', 'NumRatings'],
        table='Ratings',
        joins = [
            'JOIN Film ON Film.FilmID = Ratings.MovieID',
            'JOIN (SELECT MovieID as AvgMovieID, AVG(Rating) AS AvgRating, COUNT(*) AS NumRatings FROM Ratings GROUP BY MovieID) ON AvgMovieID = Film.FilmID'
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
