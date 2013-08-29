"""Provides base document support."""
import collections
from tavi.errors import Errors
from tavi.base.fields import BaseField

def get_field_attr(cls, field):
    """Custom function for retrieving a tavi.field attribute. Handles nested
    attributes for embedded documents as well as embedded lists of documents.

    """
    value = getattr(cls, field)
    if isinstance(value, BaseDocument):
        return value.data
    if isinstance(value, collections.MutableSequence):
        return [v.data for v in value]
    else:
        return value

class BaseDocumentMetaClass(type):
    """MetaClass for BaseDocuments. Handles initializing the list of fields for
    the BaseDocument.

    """
    def __init__(cls, name, bases, attrs):
        super(BaseDocumentMetaClass, cls).__init__(name, bases, attrs)

        cls._fields = frozenset(
            [name for name, value in attrs.iteritems() if
                isinstance(value, BaseField) and value.persist]
        )

class BaseDocument(object):
    """Base class for Mongo Documents. Provides basic field support."""
    __metaclass__ = BaseDocumentMetaClass

    def __init__(self, **kwargs):
        self._errors = Errors()
        for field in self.fields:
            setattr(self, field, kwargs.get(field, None))
            field_value = getattr(self, field)
            if hasattr(field_value, "owner"):
                field_value.owner = self

    @property
    def data(self):
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
        return list(self._fields)

    @property
    def valid(self):
        """Indicates if all the fields in the Document are valid."""
        return 0 == self.errors.count
