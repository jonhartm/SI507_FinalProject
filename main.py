import sys
from flask import Flask, render_template, request
from init_Database import ResetDatabase
from create_plotly import *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/AA_Winners', methods=['GET', 'POST'])
def AA_Winners():
    count=10
    show_nom = True
    sort="wins"
    if request.method == "POST":
        count = request.form['count']
        if count == '':
            count = 10
        show_nom = request.form.get('show_nom') # https://stackoverflow.com/questions/31859903/get-the-value-of-a-checkbox-in-flask
        sort=request.form['sort_by']
        display_graph = Graph_AAWinners(sort=sort, count=count, show_nominations=show_nom)
    else:
        #display the graph with defaults
        display_graph = Graph_AAWinners()
    return render_template(
        "AA_Winners.html",
        graph=display_graph,
        count=count,
        show_nom=show_nom,
        sort=sort
        )

@app.route('/Ratings', methods=['GET', 'POST'])
def Ratings():
    return render_template("ratings.html")

if __name__=="__main__":
    if len(sys.argv) >= 2:
        if sys.argv[1] == "--init" and len(sys.argv) == 2:
            print("Initializing the database...")
            ResetDatabase()
        else:
            print("something else")
    else:
        app.run(debug=True)
