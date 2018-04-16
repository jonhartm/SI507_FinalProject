import unittest
import sqlite3
from util import *
from init_Database import *
from load_CSV import *


class TestUtil(unittest.TestCase):
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

unittest.main()
