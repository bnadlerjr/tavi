import unittest
from pymongo import MongoClient
from tavi import Connection

class ConnectionTest(unittest.TestCase):
    def setUp(self):
        super(ConnectionTest, self).setUp()
        self.client = MongoClient()
        self.client.drop_database("test_database")
        self.db = self.client['test_database']

    def test_setup_with_host_and_port(self):
        Connection.setup("test_database", host="localhost", port=27017)
        self.assertEqual(self.db, Connection.database)

    def test_setup_with_uri(self):
        Connection.setup("test_database", host="mongodb://localhost:27017")
        self.assertEqual(self.db, Connection.database)

    def test_has_a_client_attribute(self):
        Connection.setup("test_database", host="mongodb://localhost:27017")
        self.assertEqual(self.client, Connection.client)
