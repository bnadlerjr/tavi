"""Provides support for dealing with Mongo database connections."""
from pymongo import MongoClient
from pymongo.database import Database

class Connection(object):
    """Represents a MongoDB connection."""

    def __init__(self, database_name):
        """Initializes a new connection to the specified *database_name*"""
        self._db_name = database_name

    def database(self):
        """Reference to the database for this connection."""
        return Database(MongoClient(), self._db_name)
