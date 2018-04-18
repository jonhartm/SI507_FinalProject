import sys
from flask import Flask, render_template
from init_Database import ResetDatabase
from create_plotly import *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template(
        "index.html",
        graph=GetDiv()
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
