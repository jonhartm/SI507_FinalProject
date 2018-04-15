import unittest
from util import *


class TestUtil(unittest.TestCase):
    def test_CleanJSONString(self):
        s = "'character': \"Savannah 'Vannah' Jackson\", 'credit_id'"
        self.assertEqual(CleanJSONString(s), '"character": \"Savannah (Vannah) Jackson\", "credit_id"')

        s = "'character': \"Savannah 'Vannah' Jackson\", 'character': \"Dwayne 'The Rock' Johnson\", "
        self.assertEqual(CleanJSONString(s), '"character": \"Savannah (Vannah) Jackson\", "character": \"Dwayne (The Rock) Johnson\", ')

unittest.main()
