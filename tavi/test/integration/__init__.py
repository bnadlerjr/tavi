import unittest
from tavi import Connection


class BaseMongoTest(unittest.TestCase):
    def setUp(self):
        super(BaseMongoTest, self).setUp()
        self._DB_NAME = "test_database"
        Connection.setup(self._DB_NAME)
        Connection.client.drop_database(self._DB_NAME)

        # Convenience attribute for integration tests
        self.db = Connection.client[self._DB_NAME]
