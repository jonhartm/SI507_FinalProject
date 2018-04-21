# SI507 Final Project

### Data Sources:
The Movies Dataset from Kaggle (https://www.kaggle.com/rounakbanik/the-movies-dataset)  
The Open Movie Database (http://www.omdbapi.com/)  
Wikipedia Page for Academy Award-winning Films (https://en.wikipedia.org/wiki/List_of_Academy_Award-winning_films)  
______
### How To Run:

##### Secrets.py
Before anything, you'll need to rename **secrets-CHANGEME.py** to **secrets.py** and enter in your API Key for the Open Movie Database. (You can request a key [here](http://www.omdbapi.com/apikey.aspx)).

##### Initialize The Database
Prior to running the main application, you will need to initialize the database. This is done from the command line by running "**python main.py --init**". The "--init" flag will create a new database called "movies.db", as well as a pair of .json cache files (OMDBCache.json and WikipediaCache.json). The first time it should take in the area of 90 seconds to pull all of the required data into the cache files - subsequent runs should take on the order of 30 seconds.

##### Running the Flask Application
Once the database is initialized, you can run the command "**python main.py**" from the command line, which will start a flask application on **localhost:5000**. The application can be closed by pressing Ctrl-C from the command line.

##### Data Limitations
In order to load data within a reasonable period of time, not all data is collected from the sources:
  * The Movies Dataset uses the smaller "ratings_small.csv" file, which contains a subset of about 100,000 reviews rather than the full "ratings.csv" with around 26,000,000. (Adds about 2 minutes to load)
  * The full "credits.csv" from Kaggle contains the full cast and crew for around 50,000 movies and is about 185mb. The standalone python file "createsmallcredits.py" selects a subset of around 200 films based on a SQL statement and outputs that subset to "small_credits.csv". (Adds about an hour to load)
  * Pulling data on all 50,000 films from the Open Movie Database would take far too long, and as a free user we're limited to 1,000 API calls per day. Instead, review scores, ratings, and poster images are selected from the most highly rated films, most commonly rated films, and films which have won at least one Academy Award. *(see line 37 in load_OMDBAPI.py)* If the user accesses a page that does not have information from the OMDB API, an attempt is made to fetch that data. It will be added to the cache file and the database, but any data retrieved this way will not appear after a new database initialization.

### Code Structure:
Files prefixed with "init_" and "load_" are responsible for creating and loading data into the database.
  * *init_database.py* - resets the table back to it's inital state
  * *load_CSV.py* - loads data from the CSVs from Kaggle's Movie Dataset
  * *load_OMDBAPI.py* - loads data from the Open Movie Database
  * *load_scraping.py* - scrapes the wikipedia page on Academy Award winning films  

*caching.py* contains the CacheFile class that creates and checks the cache to prevent unnessecary API or web requests.

*settings.py* contains the filenames of the CSVs that are loaded, as well as the name of the SQL database.  

*get_data.py* and *create_plotly.py* house all of the functions related to pulling data from the database and creating plotly graphs for use in the application.

*main.py* contains the flask routes and calls to templates.

*test_cases.py* is a series of unit-tests to test database initialization, data loading, and data processing.

### User Guide:
There are three links at the top of each page - "Academy Awards", "Movie Ratings", and "Budget". These each lead to a separate page with one or more graphs and tables. The information displayed in the graphs and tables can in some cases be modified with a small form. Once the form settings are changed, hit the "Refresh" button to load the new data.  
Tables will provide links to other pages where data is available: there are pages for individual Movies, Users, and Cast and Crew.
