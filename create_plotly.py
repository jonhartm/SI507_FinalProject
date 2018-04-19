import sqlite3 as sqlite
import plotly.offline as offline
import plotly.graph_objs as go
from query_builder import selectQueryBuilder
from settings import *

class PlotlyTrace():
    def __init__(self, name):
        self.name = name
        self.labels = []
        self.values = []

    def GetBar(self):
        return go.Bar(
            x = self.labels,
            y = self.values,
            name = self.name
        )

def Graph_AAWinners(sort="wins", count=10, show_nominations=True):
    conn = sqlite.connect(DATABASE_NAME)
    cur = conn.cursor()

    if sort == "noms":
        order = ['AA_Nominations DESC', 'AA_Wins DESC']
    else:
        order = ['AA_Wins DESC', 'NomNotWon DESC']

    query = selectQueryBuilder(
        columns = ['Title','Release','AA_Wins', '(AA_Nominations - AA_Wins) AS NomNotWon'],
        table = 'Film',

        order_by = order,
        limit=count
    )

    cur.execute(query)
    trace1 = PlotlyTrace("Wins")
    trace2 = PlotlyTrace("Nominations")

    for row in cur:
        trace1.labels.append(row[0])
        trace1.values.append(row[2])

        trace2.labels.append(row[0])
        trace2.values.append(row[3])

    data = [trace1.GetBar()]
    if show_nominations:
        data.append(trace2.GetBar())

    layout = go.Layout(barmode='stack')

    fig = go.Figure(data=data, layout=layout)

    return offline.plot(fig, show_link=False, output_type="div", include_plotlyjs=False)

def Graph_Ratings(sort="UserRatings", order="DESC", count=10, minimum_reviews=30):
    conn = sqlite.connect(DATABASE_NAME)
    cur = conn.cursor()

    # sub query to get the average rating by movie from the ratings table
    sub_query = selectQueryBuilder(
        columns = ['MovieID', 'AVG(Rating) AS UserRatings'],
        table = 'Ratings',
        group_by = 'MovieID',
        filter = ['COUNT(*)', '>', minimum_reviews]
    )
    query = selectQueryBuilder(
        columns = [
                'Title',
                'Release',
                'ROUND(((Rating_IMDB*10)+(Rating_RT*1)+Rating_MC)/3,2) AS AvgCriticRating', # convert all of ratings to a 100 point scale and average them out
                'ROUND(UserRatings*20,2) AS AvgUserRating', # covert the User ratings to a 100 point scale
                'ROUND(((((Rating_IMDB*10)+(Rating_RT*1)+Rating_MC)/3)-(UserRatings*20)),2) AS RatingDiff' # just AvgCriticRating-AvgUserRating
            ],
            table = 'Film',
            joins = "JOIN ("+sub_query+") ON FilmID == MovieID",
            filter = ["AvgCriticRating", "IS NOT", "NULL"],
            order_by = "{} {}".format(sort, order),
            limit = count
    )

    cur.execute(query)
    trace1 = PlotlyTrace("Average Critic Rating")
    trace2 = PlotlyTrace("Average User Rating")
    for row in cur:
        trace1.labels.append(row[0])
        trace1.values.append(row[2])

        trace2.labels.append(row[0])
        trace2.values.append(row[3])

    data = [trace1.GetBar(), trace2.GetBar()]

    layout = go.Layout(barmode="group")

    fig = go.Figure(data=data, layout=layout)

    return offline.plot(fig, show_link=False, output_type="div", include_plotlyjs=False)

# print("Top films by User Rating")
# sub_query = selectQueryBuilder(
#     columns = ['MovieID', 'AVG(Rating) AS UserRatings'],
#     table = 'Ratings',
#     group_by = 'MovieID',
#     filter = ['COUNT(*)', '>', 30]
# )
# print(selectQueryBuilder(
#     columns = [
#         'Title',
#         'Release',
#         '((Rating_IMDB*10)+(Rating_RT*1)+Rating_MC)/3 AS AvgCriticRating',
#         '(UserRatings*20) AS AvgUserRating'
#     ],
#     table = 'Film',
#     joins = "JOIN ("+sub_query+") ON FilmID == MovieID",
#     filter = ["AvgCriticRating", "IS NOT", "NULL"],
#     order_by = "UserRatings",
#     limit = ['top', 50]
# ))
