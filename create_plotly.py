import sqlite3 as sqlite
import plotly.offline as offline
import plotly.graph_objs as go
from query_builder import selectQueryBuilder
from settings import *

class BarTrace():
    def __init__(self, name):
        self.name = name
        self.labels = []
        self.values = []

    def Get(self):
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
    trace1 = BarTrace("Wins")
    trace2 = BarTrace("Nominations")

    for row in cur:
        trace1.labels.append(row[0])
        trace1.values.append(row[2])

        trace2.labels.append(row[0])
        trace2.values.append(row[3])

    data = [trace1.Get()]
    if show_nominations:
        data.append(trace2.Get())

    layout = go.Layout(barmode='stack')

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
