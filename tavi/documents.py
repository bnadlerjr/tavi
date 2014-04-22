# -*- coding: utf-8 -*-
"""Provides support for dealing with Mongo Documents."""
from bson.objectid import ObjectId
from tavi import Connection
from tavi.base.documents import BaseDocument, BaseDocumentMetaClass
from tavi.errors import TaviConnectionError
from tavi.utils.timer import Timer
import collections
import datetime
import inflection
import logging

logger = logging.getLogger(__name__)


class DocumentMetaClass(BaseDocumentMetaClass):
    """MetaClass for Documents. Sets up the database connection, infers the
    collection name by pluralizing and underscoring the class name, and sets
    the collection fo rthe Document.

    """

    def __init__(cls, name, bases, attrs):
        super(DocumentMetaClass, cls).__init__(name, bases, attrs)
        cls._collection_name = inflection.underscore(
            inflection.pluralize(name))

    @property
    def collection(cls):
        """Returns a handle to the Document collection."""
        if not Connection.database:
            raise TaviConnectionError(
                "Cannot connect to MongoDB. Did you call "
                "'tavi.connection.Connection.setup'?")
        return Connection.database[cls._collection_name]

    @property
    def collection_name(cls):
        """Returns the name of the Document collection."""
        return cls._collection_name


class Document(BaseDocument):
    """Represents a Mongo Document. Provides methods for saving and retrieving
    and deleting Documents.

    """
    __metaclass__ = DocumentMetaClass

    def __init__(self, **kwargs):
        self._id = kwargs.pop("_id", None)
        super(Document, self).__init__(**kwargs)

    @property
    def bson_id(self):
        """Returns the BSON Id of the Document."""
        return self._id

    @classmethod
    def count(cls):
        """Returns the total number of documents in the collection."""
        return cls.collection.count()

    def delete(self):
        """Removes the Document from the collection."""
        timer = Timer()
        with timer:
            result = self.__class__.collection.remove({"_id": self._id})

        logger.info(
            "(%ss) %s DELETE %s",
            timer.duration_in_seconds(),
            self.__class__.__name__,
            self._id
        )

        if result.get("err"):
            logger.error(result.get("err"))

    @classmethod
    def find(cls, *args, **kwargs):
        """Returns all Documents in collection that meet criteria. Wraps
        pymongo's *find* method and supports all of the same arguments.

        """
        timer = Timer()
        with timer:
            results = cls.collection.find(*args, **kwargs)

        logger.info(
            "(%ss) %s FIND %s, %s (%s record(s) found)",
            timer.duration_in_seconds(),
            cls.__name__,
            args,
            kwargs,
            results.count()
        )

        return [cls(**result) for result in results]

    @classmethod
    def find_all(cls):
        """Returns all Documents in collection."""
        return cls.find()

    @classmethod
    def find_by_id(cls, id_):
        """Returns the Document that matches *id_* or None if it cannot be
        found.

        """
        return cls.find_one(ObjectId(id_))

    @classmethod
    def find_one(cls, spec_or_id=None, *args, **kwargs):
        """Returns one Document that meets criteria. Wraps pymongo's find_one
        method and supports all of the same arguments.

        """
        timer = Timer()
        with timer:
            result = cls.collection.find_one(spec_or_id, *args, **kwargs)

        found_record, num_found = None, 0

        if result:
            found_record, num_found = cls(**result), 1

        logger.info(
            "(%ss) %s FIND ONE %s, %s, %s (%s record(s) found)",
            timer.duration_in_seconds(),
            cls.__name__,
            spec_or_id,
            args,
            kwargs,
            num_found
        )

        return found_record

    def save(self, w=1, wtimeout=0, j=False):
        """Saves the Document by inserting it into the collection if it does
        not exist or updating it if it does. Returns True if save was
        successful. Ensures that the Document is valid before saving and
        returns False if it was not.

        This function performs an upsert if the model has an ID, but is not in
        the database.

        If the document model has a field named 'created_at', this field's
        value will be set to the current time when the document is inserted.

        Supports the following arguments that are passed to pymongo:

        w: Write concern level. Default is 1
        wtimeout: Timeout in ms for write concern. Default is 0
        j: Journaling option for write concern. Default is False

        See Pymongo docs for more information on these arguments:
        http://api.mongodb.org/python/current/api/pymongo/collection.html

        See the Mongo docs for more information on Write Concern:
        http://docs.mongodb.org/manual/core/write-concern/

        """
        if not self.valid:
            return False

        collection = self.__class__.collection
        timer = Timer()
        operation = None

        write_opts = frozenset(["w", "j", "wtimeout"])
        kwargs = {k: v for k, v in locals().iteritems() if k in write_opts}

        now = datetime.datetime.utcnow()
        self.__update_timestamps("last_modified_at", now)

        if self.bson_id:
            operation = "UPDATE"
            with timer:
                result = collection.update(
                    {"_id": self._id},
                    {"$set": self.mongo_field_values},
                    upsert=True,
                    **kwargs
                )

            if result.get("err"):
                logger.error(result.get("err"))

        else:
            operation = "INSERT"
            self.__update_timestamps("created_at", now)

            with timer:
                self._id = collection.insert(self.mongo_field_values, **kwargs)

        self.changed_fields = set()

        logger.info(
            "(%ss) %s %s %s, %s",
            timer.duration_in_seconds(),
            self.__class__.__name__,
            operation,
            self.mongo_field_values,
            self._id
        )
        return True

    def __update_timestamps(self, name, timestamp):
        # TODO: Should this be pulled out into a generic function? i.e.
        #       set_nested_field_attr(cls, field, value)
        for field in self.fields:
            value = getattr(self, field)
            if name == field:
                setattr(self, name, timestamp)
            elif isinstance(value, collections.Iterable):
                for item in value:
                    if isinstance(item, EmbeddedDocument):
                        setattr(item, name, timestamp)
            elif isinstance(value, EmbeddedDocument):
                setattr(value, name, timestamp)


class EmbeddedDocument(BaseDocument):
    """Represents a single EmbeddedDocument. Supports an *owner* attribute that
    indicates the owning Document.

    """
    def __init__(self, **kwargs):
        super(EmbeddedDocument, self).__init__(**kwargs)
        self.owner = None

    def __eq__(self, other):
        return other and self.field_values == other.field_values
