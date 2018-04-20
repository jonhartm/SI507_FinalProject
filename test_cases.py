#-------------------------------------------------------------------------------
# TEST_CASES.PY
# Unit tests to cover database initailization, loading, and data processing
#-------------------------------------------------------------------------------

import unittest
import sqlite3
import os
import os.path
from bs4 import BeautifulSoup, SoupStrainer
from util import *
from init_Database import *
from load_CSV import *
from load_OMDBAPI import *
from get_data import *
from secrets import *
from settings import *

class TestDatabaseInitialize(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ResetDatabase()

    def test_DataFilesPresent(self):
        self.assertTrue(os.path.exists(MOVIEMETADATA_CSV))
        self.assertTrue(os.path.exists(CREDITS_CSV))
        self.assertTrue(os.path.exists(RATINGS_CSV))

    def test_SecretsFilePresent(self):
        self.assertTrue(os.path.exists("secrets.py"))
        self.assertTrue(OMDB_API_KEY is not '')

    def test_FilmTable(self):
        with sqlite.connect(DATABASE_NAME) as conn:
            cur = conn.cursor()

            statement = "SELECT COUNT(*) FROM Film"
            cur.execute(statement)
            self.assertEqual(cur.fetchone()[0], 45401)

            statement = "SELECT FilmID, Title, Release, Budget, Revenue, Runtime FROM Film WHERE FilmID == 11"
            cur.execute(statement)
            result = cur.fetchone()
            self.assertEqual(result, (11, "Star Wars", "1977-05-25", 11000000, 775398007, 121))

            statement = "SELECT FilmID, Title, Release, Budget, Revenue, Runtime FROM Film ORDER BY Revenue DESC LIMIT 1"
            cur.execute(statement)
            result = cur.fetchone()
            self.assertEqual(result, (19995, "Avatar", "2009-12-10", 237000000, 2787965087, 162))

    def test_OMDBUpdates(self):
        with sqlite.connect(DATABASE_NAME) as conn:
            cur = conn.cursor()

            # check an update that had all three review scores
            statement = "SELECT Rating_IMDB, Rating_RT, Rating_MC FROM Film WHERE FilmID = 597"
            cur.execute(statement)
            result = cur.fetchone()
            self.assertEqual(result, (7.8, "88%", 75))

            # check an update that was missing review scores
            statement = "SELECT Rating_IMDB, Rating_RT, Rating_MC FROM Film WHERE FilmID = 914"
            cur.execute(statement)
            result = cur.fetchone()
            self.assertEqual(result, (8.5, "92%", None))

    def test_WikipediaScrape(self):
        with sqlite.connect(DATABASE_NAME) as conn:
            cur = conn.cursor()

            # check an update that had all three fields
            statement = "SELECT BestPicture, AA_Wins, AA_Nominations FROM Film WHERE FilmID = 665"
            cur.execute(statement)
            result = cur.fetchone()
            self.assertEqual(result, (1,11,12))

            # check an update that only had a single field
            statement = "SELECT BestPicture, AA_Wins, AA_Nominations FROM Film WHERE FilmID = 862"
            cur.execute(statement)
            result = cur.fetchone()
            self.assertEqual(result, (None, 0, 3))

    def test_CreditsTables(self):
        with sqlite.connect(DATABASE_NAME) as conn:
            cur = conn.cursor()

            # check an update that had all three fields
            statement = '''
            SELECT COUNT(*) FROM CastByFilm
            	JOIN People ON People.ID == CastByFilm.CastID
            	JOIN Role ON Role.ID == CastByFilm.RoleID
            	JOIN Film ON Film.FilmID == CastByFilm.FilmID
            WHERE Role.Title == "Director"
            '''
            cur.execute(statement)
            result = cur.fetchone()
            self.assertEqual(result[0], 212)

            statement = '''
            SELECT COUNT(*) FROM CastByFilm
            	JOIN People ON People.ID == CastByFilm.CastID
            	JOIN Role ON Role.ID == CastByFilm.RoleID
            	JOIN Film ON Film.FilmID == CastByFilm.FilmID
            WHERE Role.Title= "Cast" AND Name = "Tom Hanks"
            '''
            cur.execute(statement)
            result = cur.fetchone()
            self.assertEqual(result[0], 5)

            statement = '''
            SELECT DISTINCT Film.Title, People.Name, Role.Title FROM CastByFilm
            	JOIN People ON People.ID == CastByFilm.CastID
            	JOIN Role ON Role.ID == CastByFilm.RoleID
            	JOIN Film ON Film.FilmID == CastByFilm.FilmID
            WHERE Role.Title == "Director" AND Name = "Martin Scorsese"
            ORDER BY Film.Title
            LIMIT 1
            '''
            cur.execute(statement)
            result = cur.fetchone()
            self.assertEqual(result, ("Hugo", "Martin Scorsese", "Director"))

    @classmethod
    def tearDownClass(cls):
        pass

class TestCaching(unittest.TestCase):
    def setUp(self):
        self.cache = CacheFile("test_cache.json", print_info=True)

    def test_APICaching(self):
        # test making an API call with an empty cache file
        url = 'http://www.omdbapi.com'
        params = {'apikey':OMDB_API_KEY, "t":"Braveheart", "y":"1995"}
        response = self.cache.CheckCache_API(url, params)
        self.assertIsInstance(response, dict)
        self.assertEqual(response['Title'], "Braveheart")
        self.assertEqual(response['Released'], "24 May 1995")

        # test making an API call with a cache file that contains information
        params = {'apikey':OMDB_API_KEY, "t":"Toy Story", "y":"1995"}
        response = self.cache.CheckCache_API(url, params)
        self.assertIsInstance(response, dict)
        self.assertEqual(response['Title'], "Toy Story")
        self.assertEqual(response['Released'], "22 Nov 1995")

        # test making an identical API call
        params = {'apikey':OMDB_API_KEY, "t":"Toy Story", "y":"1995"}
        response = self.cache.CheckCache_API(url, params)
        self.assertIsInstance(response, dict)
        self.assertEqual(response['Title'], "Toy Story")
        self.assertEqual(response['Released'], "22 Nov 1995")

        # test making an API call with specific keys to store
        params = {'apikey':OMDB_API_KEY, "t":"Titanic", "y":"1997"}
        response = self.cache.CheckCache_API(url, params, keys=["Title", "Director"])
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 2)
        self.assertEqual(response['Title'], "Titanic")
        self.assertEqual(response['Director'], "James Cameron")
        with self.assertRaises(KeyError):
            x = response['Released']

        # duplicate API call to check that only the requested keys were stored
        params = {'apikey':OMDB_API_KEY, "t":"Titanic", "y":"1997"}
        response = self.cache.CheckCache_API(url, params, keys=["Title", "Director"])
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 2)
        self.assertEqual(response['Title'], "Titanic")
        self.assertEqual(response['Director'], "James Cameron")
        with self.assertRaises(KeyError):
            x = response['Released']

    def test_WebScrapingCaching(self):
        # check creating a soup with nothing in the cache
        url = "http://www.something.com/"
        response = self.cache.CheckCache_Soup(url)
        self.assertIsInstance(response, BeautifulSoup)
        self.assertEqual(response.find("body").text, "Something.")

        # check creating a soup from an item that's already in the cache
        response = self.cache.CheckCache_Soup(url)
        self.assertIsInstance(response, BeautifulSoup)
        self.assertEqual(response.find("body").text, "Something.")

        # check creating a soup with a SoupStrainer
        url = "http://books.toscrape.com/"
        response = self.cache.CheckCache_Soup(url, strainer=SoupStrainer(class_="product_pod"))
        self.assertEqual(len(response), 41)

    def tearDown(self):
        os.remove("test_cache.json")

class TestUtil(unittest.TestCase):
    def test_GetString(self):
        s = "{'cast_id': 14, 'character': 'Woody (voice)', 'credit_id': '52fe4284c3a36847f8024f95', 'gender': 2, 'id': 31, 'name': 'Tom Hanks', 'order': 0, 'profile_path': '/pQFoyx7rp09CJTAb932F2g8Nlho.jpg'}"
        self.assertEqual(GetString(s, "credit_id"), "52fe4284c3a36847f8024f95")
        self.assertEqual(GetString(s, "name"), "Tom Hanks")
        self.assertEqual(GetString(s, "cast_id", False), "14")

    def test_CleanJSONString(self):
        s = "{'cast_id': 14, 'character': 'Woody (voice)', 'credit_id': '52fe4284c3a36847f8024f95', 'gender': 2, 'id': 31, 'name': 'Tom Hanks', 'order': 0, 'profile_path': '/pQFoyx7rp09CJTAb932F2g8Nlho.jpg'}"
        parsed_json = CleanJSONString(s)
        self.assertEqual(parsed_json['name'], "Tom Hanks")

        s = "{'cast_id': 95, 'character': \"Casals' Date\", 'credit_id': '56be7708c3a36817f200504f', 'gender': 1, 'id': 106714, 'name': 'Kimberly Flynn', 'order': 49, 'profile_path': None}"
        parsed_json = CleanJSONString(s)
        self.assertEqual(parsed_json['name'], 'Kimberly Flynn')

        s = "{'cast_id': 26, 'character': '\"Jack Jones\"', 'credit_id': '52fe43c59251416c7501d751', 'gender': 2, 'id': 6840, 'name': 'Larry Hagman', 'order': 16, 'profile_path': '/40PVsGp5Wp5kbUhAefLHqjqbarc.jpg'}"
        parsed_json = CleanJSONString(s)
        self.assertEqual(parsed_json['name'], "Larry Hagman")

        s = "{'cast_id': 28, 'character': 'Sgt. Jeffrey \"Jeff\" Rabin', 'credit_id': '52fe4260c3a36847f8019b0b', 'gender': 2, 'id': 6486, 'name': 'Dan Hedaya', 'order': 9, 'profile_path': '/5E4SUVfLMUKNCiP0dMhyOv3XHVZ.jpg'}"
        parsed_json = CleanJSONString(s)
        self.assertEqual(parsed_json['name'], "Dan Hedaya")

        s = "{'credit_id': '52fe4284c3a36847f8024f49', 'department': 'Directing', 'gender': 2, 'id': 7879, 'job': 'Director', 'name': 'John Lasseter', 'profile_path': '/7EdqiNbr4FRjIhKHyPPdFfEEEFG.jpg'}"
        parsed_json = CleanJSONString(s)
        self.assertEqual(parsed_json['name'], "John Lasseter")
        self.assertEqual(parsed_json['job'], "Director")

        s = "{'credit_id': '589214099251412dc5009d57', 'department': 'Art', 'gender': 0, 'id': 1748710, 'job': 'Set Dresser', 'name': \"Kelly O'Connell\", 'profile_path': None}"
        parsed_json = CleanJSONString(s)
        self.assertEqual(parsed_json['name'], "Kelly O'Connell")
        self.assertEqual(parsed_json['job'], "Set Dresser")

        s = "{'credit_id': '52fe44959251416c75039e3b', 'department': 'Camera', 'gender': 2, 'id': 492, 'job': 'Director of Photography', 'name': 'Janusz Kamiński', 'profile_path': '/5LNGARjEfMDOcEP6fMNtJypAGYx.jpg'}"
        parsed_json = CleanJSONString(s)
        self.assertEqual(parsed_json['name'], "Janusz Kamiński")
        self.assertEqual(parsed_json['job'], "Director of Photography")

class TestGetData(unittest.TestCase):
    def test_CastAndCrew(self):
        # function should return a list of tuples
        moonlight_data = GetCastAndCrew("Moonlight", "2016")
        self.assertIsInstance(moonlight_data, list)
        self.assertIsInstance(moonlight_data[0], tuple)
        # check specific items in the data
        self.assertEqual(moonlight_data[0], (10789, 'Trevante Rhodes', 'Cast', None))
        self.assertEqual(len(moonlight_data), 110)

        # function should return None if there is no data present
        nonsense_data = GetCastAndCrew("DFGSDFGSDFGSDFG", "2525")
        self.assertEqual(nonsense_data, None)

        # function should accept either a string or an integer for the year
        moonlight_data = GetCastAndCrew("Moonlight", 2016)
        self.assertEqual(len(moonlight_data), 110)

    def test_GetMoviesByPerson(self):
        # function should return a list of tuples
        thanks = GetMoviesByPerson(164)
        self.assertIsInstance(thanks, list)
        self.assertIsInstance(thanks[0], tuple)
        # check specific items in the data
        self.assertEqual(thanks[0], ('Tom Hanks', 'Apollo 13', '1995-06-30', 'Cast'))
        self.assertEqual(len(thanks), 5)

        # function should return None if there is no data present
        nonsense_data = GetMoviesByPerson(-1)
        self.assertEqual(nonsense_data, None)

    def test_GetReviewsByUser(self):
        # function should return a list of tuples
        rand_user = GetReviewsByUser(164)
        self.assertIsInstance(rand_user, UserReviews)
        self.assertIsInstance(rand_user.data[0], tuple)
        # check specific items in the data
        self.assertEqual(rand_user.data[0], ('Mission: Impossible', '1996-05-22', 5, 4.23, 0.77, 31))
        self.assertEqual(len(rand_user), 44)
        self.assertEqual(rand_user.getAvgRating(), 3.67)
        self.assertEqual(rand_user.getAvgDifference(), -0.132)

        # check that sorting works correctly
        self.assertEqual(rand_user.getData()[0][0], "Mission: Impossible")
        self.assertEqual(rand_user.getData(order="asc")[0][0], "Grbavica")

        self.assertEqual(rand_user.getData("AvgUserRating")[0][0], "The Million Dollar Hotel")
        self.assertEqual(rand_user.getData("AvgUserRating", order="asc")[0][0], "Grbavica")

        self.assertEqual(rand_user.getData("Difference")[0][0], "Point Break")
        self.assertEqual(rand_user.getData("Difference", order="asc")[0][0], "Grbavica")

        # function should return None if there is no data present
        nonsense_data = GetReviewsByUser(-1)
        self.assertEqual(nonsense_data, None)

    def test_MovieDetails(self):
        movie = MovieDetails("Titanic", "1997")
        self.assertEqual(movie.title, "Titanic")
        self.assertEqual(movie.release, "1997-11-18")
        self.assertEqual(movie.budget, 200000000)
        self.assertEqual(movie.revenue, 1845034188)
        self.assertEqual(movie.runtime, 194)
        self.assertEqual(movie.rating, "PG-13")
        self.assertEqual(movie.total_reviews, 147)

        # check the formatting for currency style fields
        self.assertEqual(movie.getBudget(), '$200,000,000.00')
        self.assertEqual(movie.getRevenue(), '$1,845,034,188.00')
        self.assertEqual(movie.getProfit(), '$1,645,034,188.00')

unittest.main()
