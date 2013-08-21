import unittest
from pymongo import MongoClient
from pymongo.database import Database

class BaseMongoTest(unittest.TestCase):
    def setUp(self):
        super(BaseMongoTest, self).setUp()
        self._DB_NAME = "test_database"
        client = MongoClient()
        client.drop_database(self._DB_NAME)
        self.db = client[self._DB_NAME]
