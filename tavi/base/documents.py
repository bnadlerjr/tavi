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

class BaseDocumentMetaClass(type):
    """MetaClass for BaseDocuments. Handles initializing the list of fields for
    the BaseDocument.

    """
    def __init__(cls, name, bases, attrs):
        super(BaseDocumentMetaClass, cls).__init__(name, bases, attrs)

        sorted_fields = sorted(
            [field for field in attrs.iteritems() if isinstance(field[1],
                BaseField) and field[1].persist],
            key = lambda i: i[1].creation_order
        )

        cls._field_descriptors = collections.OrderedDict(sorted_fields)

class BaseDocument(object):
    """Base class for Mongo Documents. Provides basic field support."""
    __metaclass__ = BaseDocumentMetaClass

    def __init__(self, **kwargs):
        self._errors = Errors()
        for field in self.fields:
            field_descriptor = self._field_descriptors[field]
            field_default = field_descriptor.default

            field_descriptor.setFieldOnObject(self, kwargs.get(field))

            field_value = getattr(self, field)
            if hasattr(field_value, "owner"):
                field_value.owner = self

    @property
    def field_values(self):
        """Returns a dictionary containing all fields and their values."""
        return { field: get_field_attr(self, field) for field in self.fields }

    @property
    def errors(self):
        """Returns a tavi.Errors object that contains any errors for the
        Document.

        """
        return self._errors

    @property
    def fields(self):
        """Returns the list of fields for the Document."""
        return self._field_descriptors.keys()

    @property
    def valid(self):
        """Indicates if all the fields in the Document are valid."""
        return 0 == self.errors.count

    def to_json(self, fields=None):
        """Convert Document model object to JSON. Optionally, specify which
        fields should be serialized.

        """
        if fields:
            return dumps({ field: self.field_values[field] for field in fields })
        else:
            return dumps(self.field_values)

    @classmethod
    def from_json(cls, json_str):
        """Deserialize a JSON string into a Document model object."""
        attrs = loads(json_str)
        return cls(**attrs)
