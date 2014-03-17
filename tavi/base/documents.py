# -*- coding: utf-8 -*-
"""Provides base document support."""
import collections
from bson.json_util import dumps, loads
from tavi.errors import Errors
from tavi.base.fields import BaseField


def get_field_attr(cls, field):
    """Custom function for retrieving a tavi.field attribute. Handles nested
    attributes for embedded documents as well as embedded lists of documents.

    """
    value = getattr(cls, field)
    if isinstance(value, BaseDocument):
        return value.field_values
    if isinstance(value, collections.MutableSequence):
        return [v.field_values for v in value]
    else:
        return value


def set_field_attr(cls, field, value):
    """Custom function for setting a tavi.field attribute."""
    field_descriptor = cls._field_descriptors[field]

    if isinstance(value, collections.MutableSequence):
        for item in value:
            getattr(cls, field).append(field_descriptor._type(**item))
        return

    if None == value:
        value = field_descriptor.default

    if isinstance(value, dict):
        value = field_descriptor.doc_class(**value)

    setattr(cls, field, value)


class BaseDocumentMetaClass(type):
    """MetaClass for BaseDocuments. Handles initializing the list of fields for
    the BaseDocument.

    """
    def __init__(cls, name, bases, attrs):
        super(BaseDocumentMetaClass, cls).__init__(name, bases, attrs)

        sorted_fields = sorted(
            [field for field in attrs.iteritems()
                if isinstance(field[1], BaseField) and field[1].persist],
            key=lambda i: i[1].creation_order
        )

        cls._field_descriptors = collections.OrderedDict(sorted_fields)


class BaseDocument(object):
    """Base class for Mongo Documents. Provides basic field support."""
    __metaclass__ = BaseDocumentMetaClass

    def __init__(self, **kwargs):
        self._errors = Errors()
        for field in self.fields:
            set_field_attr(self, field, kwargs.get(field))
        self.changed_fields = set()

    @property
    def fields(self):
        """Returns the list of fields for the Document."""
        return self._field_descriptors.keys()

    @property
    def field_values(self):
        """Returns a dictionary containing all fields and their values."""
        return {field: get_field_attr(self, field) for field in self.fields}

    @property
    def mongo_field_values(self):
        """Same as field_values except uses the Mongo field names. This way
        the document can have a field name that is different from the
        field name persisted in Mongo.

        """
        return {
            v.name: get_field_attr(self, k)
            for k, v in self._field_descriptors.items()
        }

    @property
    def errors(self):
        """Returns a tavi.Errors object that contains any errors for the
        Document.

        """
        return self._errors

    @property
    def valid(self):
        """Indicates if all the fields in the Document are valid."""
        self.__validate__()
        return 0 == self.errors.count

    def to_json(self, fields=None):
        """Convert Document model object to JSON. Optionally, specify which
        fields should be serialized.

        """
        include_bson_id = True

        if fields:
            if "bson_id" not in fields:
                include_bson_id = False
            else:
                fields.remove("bson_id")

            field_map = {field: self.field_values[field] for field in fields}
        else:
            field_map = self.field_values

        if include_bson_id:
            field_map["id"] = self.bson_id

        return dumps(field_map)

    @classmethod
    def from_json(cls, json_str):
        """Deserialize a JSON string into a Document model object."""
        attrs = loads(json_str)
        return cls(**attrs)

    def __validate__(self):
        """Override for model level validations. This method will be called by
        the #valid property.

        """
        pass
