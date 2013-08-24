"""Provides support for dealing with Mongo database connections."""
from pymongo import MongoClient
from pymongo.database import Database

class Connection(object):
    """Represents a MongoDB connection."""

    client   = None
    database = None

    @classmethod
    def setup(cls, database_name, **kwargs):
        """Sets ups the Mongo connection. *database_name* is the name of the
        database to connect to. **kwargs** are the same options that can be
        passed to *MongoClient*.

        """
        client = MongoClient(**kwargs)
        cls.client = client
        cls.database = Database(client, database_name)
