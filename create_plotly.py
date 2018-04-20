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
        self.hovertext = []

class PlotlyBarTrace(PlotlyTrace):
    def GetBar(self):
        return go.Bar(
            x = self.labels,
            y = self.values,
            name = self.name,
            text=self.hovertext
        )

class PlotlyBoxTrace(PlotlyTrace):
    def GetBox(self):
        return go.Box(
            x=self.values,
            name=self.name,
            boxmean='sd'
        )

class PlotlyScatterTrace(PlotlyTrace):
    def __init__(self, name):
        self.name = name
        self.x = []
        self.y = []
        self.mode = "markers"

    def GetScatter(self):
        return go.Scatter(
            x = self.x,
            y = self.y,
            mode = self.mode
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
    trace1 = PlotlyBarTrace("Wins")
    trace2 = PlotlyBarTrace("Nominations")
    raw_data = []

    for row in cur:
        trace1.labels.append("{} ({})".format(row[0], row[1]))
        trace1.values.append(row[2])

        trace2.labels.append("{} ({})".format(row[0], row[1]))
        trace2.values.append(row[3])

        raw_data.append(row)

    data = [trace1.GetBar()]
    if show_nominations:
        data.append(trace2.GetBar())

    if sort=="wins":
        title = "Top {} films with the most Academy Award Wins".format(count)
    else:
        title = "Top {} films with the most Academy Award Nominations".format(count)

    layout = go.Layout(
        barmode='stack',
        title=title
        )

    fig = go.Figure(data=data, layout=layout)

    return offline.plot(fig, show_link=False, output_type="div", include_plotlyjs=False), raw_data

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
                'ABS(ROUND(((((Rating_IMDB*10)+(Rating_RT*1)+Rating_MC)/3)-(UserRatings*20)),2)) AS RatingDiff ' # just ABS(AvgCriticRating-AvgUserRating)
            ],
            table = 'Film',
            joins = "JOIN ("+sub_query+") ON FilmID == MovieID",
            filter = ["AvgCriticRating", "IS NOT", "NULL"],
            order_by = "{} {}".format(sort, order),
            limit = count
    )

    cur.execute(query)
    trace1 = PlotlyBarTrace("Average Critic Rating")
    trace2 = PlotlyBarTrace("Average User Rating")
    raw_data = []
    for row in cur:
        trace1.labels.append("{} ({})".format(row[0], row[1]))
        trace1.values.append(row[2])

        trace2.labels.append("{} ({})".format(row[0], row[1]))
        trace2.values.append(row[3])

        raw_data.append(row)

    data = [trace1.GetBar(), trace2.GetBar()]

    layout = go.Layout(
        barmode="group",
        title="Avg Critic Rating VS Avg User Rating"
        )

    fig = go.Figure(data=data, layout=layout)

    return offline.plot(fig, show_link=False, output_type="div", include_plotlyjs=False), raw_data

def Graph_MovieRatings(title, year):
    conn = sqlite.connect(DATABASE_NAME)
    cur = conn.cursor()

    sub_query = selectQueryBuilder(
        columns = 'FilmID',
        table = 'Film',
        filter = [['Title', "=", title], "AND", ['Release', 'LIKE', year+'%']]
    )
    query = selectQueryBuilder(
        columns = ['UserID', 'Rating', 'datetime(Timestamp, \'unixepoch\') As Date'], #https://stackoverflow.com/questions/14629347/how-to-convert-unix-epoch-time-in-sqlite
        table = 'Ratings',
        filter = ['MovieID', '=', "("+sub_query+")"],
        order_by = "Date DESC"
    )

    cur.execute(query)
    boxtrace = PlotlyBoxTrace("User Ratings")
    scattertrace = PlotlyScatterTrace("User Ratings")

    raw_data = []
    for row in cur:
        boxtrace.values.append(row[1])
        scattertrace.x.append(row[2])
        scattertrace.y.append(row[1])
        raw_data.append(row)

    box_data = [boxtrace.GetBox()]
    box_layout = go.Layout(
        title="User Ratings for {} ({})".format(title, year)
    )
    box_fig = go.Figure(data=box_data, layout=box_layout)

    scatter_data = [scattertrace.GetScatter()]
    scatter_layout = go.Layout(
        title="User Ratings Over Time for {} ({})".format(title, year)
    )
    scatter_fig = go.Figure(data=scatter_data, layout=scatter_layout)

    if len(raw_data) == 0:
        raw_data = None

    return offline.plot(box_fig, show_link=False, output_type="div", include_plotlyjs=False), offline.plot(scatter_fig, show_link=False, output_type="div", include_plotlyjs=False), raw_data

def Graph_BudgetPerStar():
    conn = sqlite.connect(DATABASE_NAME)
    cur = conn.cursor()

    subquery = selectQueryBuilder(
        columns = ['MovieId AS RatingMovieID', 'AVG(Rating) AS UserRating'],
        table = 'Ratings',
        group_by = 'MovieID',
        filter = ["COUNT(*)", ">", 30]
    )

    query = selectQueryBuilder(
        columns = ['Title', 'Release', 'Budget', 'ROUND(UserRating, 2) AS AvgUserRating', 'ROUND(Budget/UserRating, 2) AS DollarsPerStar'],
        table = 'Film',
        joins = 'JOIN ('+subquery+') ON RatingMovieID = Film.FilmID',
        filter = ['Budget', '>', 100000],
        order_by = 'DollarsPerStar DESC',
        limit = 30
    )

    cur.execute(query)
    trace = PlotlyBarTrace("Dollars Per Star")
    raw_data = []
    for row in cur:
        trace.values.append(row[4])
        trace.hovertext.append("{} ({})<br>{} for {} stars".format(row[0], row[1][:4], '${:,.0f}'.format(row[2]), row[3]))
        trace.labels.append(row[0])
        row = list(row)
        row[2] = '${:,.0f}'.format(row[2])
        row[4] = '${:,.0f}'.format(row[4])
        raw_data.append(row)

    data = [trace.GetBar()]
    layout = go.Layout(
        title="Dollars Spent Per Star (User Reviews)"
    )
    fig = go.Figure(data=data, layout=layout)
    return offline.plot(fig, show_link=False, output_type="div", include_plotlyjs=False), raw_data

def Graph_RatingCount(rating_data):
    ratings = []
    for row in rating_data:
        ratings.append(row[2])

    conn = sqlite.connect(DATABASE_NAME)
    cur = conn.cursor()
    query = "SELECT Rating FROM Ratings"
    cur.execute(query)
    overall_ratings = []
    for row in cur:
        overall_ratings.append(row[0])

    data = [
        go.Histogram(x=ratings, histnorm='probability', opacity=0.5, name="User Ratings"),
        go.Histogram(x=overall_ratings, histnorm='probability', opacity=0.5, name="Overall Ratings")
        ]

    layout = go.Layout(
        title="User Rating Count ({} Ratings)".format(len(rating_data)),
        barmode='overlay'
    )

    fig = go.Figure(data=data, layout=layout)
    return offline.plot(fig, show_link=False, output_type="div", include_plotlyjs=False)
