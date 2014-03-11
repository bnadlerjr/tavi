# -*- coding: utf-8 -*-
"""A simple Object Document Mapper for MongoDB"""
from pymongo import MongoClient, MongoReplicaSetClient
from pymongo.database import Database
import collections
import tavi


class Connection(object):
    """Represents a MongoDB connection."""

    client = None
    database = None

    @classmethod
    def setup(cls, database_name, **kwargs):
        """Sets ups the Mongo connection. *database_name* is the name of the
        database to connect to. **kwargs** are the same options that can be
        passed to *MongoClient*. If replicaSet is present in the host, a
        *MongoReplicaSetClient* will be used instead.

        """
        host = kwargs.get("host", "")
        if host.find("replicaSet") > 0:
            client = MongoReplicaSetClient(**kwargs)
        else:
            client = MongoClient(**kwargs)
        cls.client = client
        cls.database = Database(client, database_name)


class EmbeddedList(collections.MutableSequence):
    """A custom list for embedded documents. Ensures that only
    EmbeddedDocuments can be added to the list. Supports all the of standard
    list functions, excluding sorting.

    """
    def __init__(self, name, type_):
        self.list_ = list()
        self.name = name
        self._owner = None
        self._type = type_

        if not isinstance(self._type(), tavi.documents.EmbeddedDocument):
            raise tavi.errors.TaviTypeError(
                "tavi.EmbeddedList only accepts "
                "tavi.document.EmbeddedDocument objects"
            )

    def __len__(self):
        return len(self.list_)

    def __getitem__(self, index):
        return self.list_[index]

    def __delitem__(self, index):
        del self.list_[index]

    def __repr__(self):
        return str(self.list_)

    def __setitem__(self, index, value):
        self.list_[index] = value

    def __eq__(self, other):
        return self.list_ == other

    @property
    def owner(self):
        """The object that owns this list."""
        return self._owner

    @owner.setter
    def owner(self, value):
        """Sets the owner of the list. Raises a TaviTypeError if *value* does
        not inherit from tavi.base.document.BaseDocument.

        """
        if not isinstance(value, tavi.base.documents.BaseDocument):
            raise tavi.errors.TaviTypeError(
                "owner must be of type or inherit from "
                "tavi.base.document.BaseDocument"
            )

        self._owner = value

    def find(self, item):
        """Finds *item* in the list and returns it. If not found, returns
        None.

        """
        return next((i for i in self.list_ if i == item), None)

    def insert(self, index, value):
        """Adds *value* to list at *index*. Ensures that *value* is a
        tavi.document.EmbeddedDocument and raises a TaviTypeError if it is
        not. Checks that *value* is valid before being added. If *value* is not
        valid it adds the errors to the list owner.

        """
        if not isinstance(value, self._type):
            raise tavi.errors.TaviTypeError(
                "This tavi.EmbeddedList only accepts items of type %s (tried "
                "to add an object of type %s)" % (
                    self._type().__class__.__name__, value.__class__.__name__
                )
            )

        if value.valid:
            value.owner = self.owner
            self.list_.insert(index, value)
        else:
            for msg in value.errors.full_messages:
                self.owner.errors.add("%s Error:" % self.name, msg)
