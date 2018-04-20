import sys
from flask import Flask, render_template, request
from init_Database import ResetDatabase
from get_data import *
from create_plotly import *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/AA_Winners', methods=['GET', 'POST'])
def AA_Winners():
    sort="wins"
    count=10
    show_nom = True
    # if there was a post, alter any of the graph params based on that
    if request.method == "POST":
        count = request.form['count']
        if count == '':
            count = 10
        show_nom = request.form.get('show_nom') # https://stackoverflow.com/questions/31859903/get-the-value-of-a-checkbox-in-flask
        sort=request.form['sort_by']

    display_graph, raw_data = Graph_AAWinners(sort=sort, count=count, show_nominations=show_nom)
    return render_template(
        "AA_Winners.html",
        graph=display_graph,
        raw_data=raw_data,
        count=count,
        show_nom=show_nom,
        sort=sort
        )

@app.route('/Ratings', methods=['GET', 'POST'])
def Ratings():
    sort="AvgCriticRating"
    order="DESC"
    count=10
    minimum_reviews=30
    if request.method == "POST":
        sort = request.form['sort_by']
        order = request.form['ordering']
        count = request.form['count']

    display_graph, raw_data = Graph_Ratings(
        sort=sort,
        order=order,
        count=count,
        minimum_reviews=minimum_reviews
        )
    return render_template(
        "ratings.html",
        graph=display_graph,
        raw_data=raw_data,
        order=order,
        sort=sort,
        count=count
        )

@app.route('/Budget', methods=['GET', 'POST'])
def Budgets():
    budget_sort = "Budget"
    budget_limit = 20
    if request.method == "POST":
        budget_sort = request.form['budget_sort']
        budget_limit = request.form['budget_limit']
    dollars_per_star_graph, dps_raw_data = Graph_BudgetPerStar()
    budget_graph, budget_raw_data = Graph_Budget(budget_sort, budget_limit)
    return render_template(
        "budget.html",
        budget_sort=budget_sort,
        budget_limit=budget_limit,
        budget_graph=budget_graph,
        budget_raw_data=budget_raw_data,
        dps_graph=dollars_per_star_graph,
        dps_raw_data=dps_raw_data
    )

@app.route('/Movie/<title>/<year>')
def Movie(title, year):
    boxgraph_ratings, scattergraph_ratings, raw_data_ratings = Graph_MovieRatings(
        title=title,
        year=year
    )
    details = MovieDetails(title, year)
    return render_template(
        "movie.html",
        details=details,
        boxgraph=boxgraph_ratings,
        scattergraph=scattergraph_ratings,
        ratings_data=raw_data_ratings,
        cast_crew_data=GetCastAndCrew(title, year)
        )

@app.route('/Person/<id>')
def Person(id):
    role_data = GetMoviesByPerson(id)
    return render_template(
        "person.html",
        person=role_data[0][0],
        role_data=role_data
    )

@app.route('/User/<id>', methods=['GET', 'POST'])
def User(id):
    sort="UserRating"
    order="desc"
    ratings_data=GetReviewsByUser(id)
    rating_counts=Graph_RatingCount(ratings_data.getData())
    if request.method == "POST":
        sort = request.form['sort_by']
        order = request.form['ordering']
    return render_template(
    "user.html",
    id=id,
    rating_counts=rating_counts,
    ratings=ratings_data,
    sort=sort,
    order=order
    )

if __name__=="__main__":
    if len(sys.argv) >= 2:
        if sys.argv[1] == "--init" and len(sys.argv) == 2:
            print("Initializing the database...")
            ResetDatabase()
        else:
            print("something else")
    else:
        app.run(debug=True)
