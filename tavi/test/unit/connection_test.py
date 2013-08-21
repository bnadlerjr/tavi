import unittest
from pymongo import MongoClient
from tavi.connection import Connection

class ConnectionTest(unittest.TestCase):
    def test_get_database(self):
        client = MongoClient()
        client.drop_database("test_database")
        db = client['test_database']

        cnn = Connection("test_database")
        self.assertEqual(db, cnn.database())
