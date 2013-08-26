"""Provides various field types."""
import re
import datetime
from tavi.embedded_list import EmbeddedList
from tavi.base.field import BaseField
from tavi.document import EmbeddedDocument
from tavi.errors import TaviTypeError

class DateTimeField(BaseField):
    """Represents a naive datetime for a Mongo Document.
    Supports all the validations in *BaseField*.

    """
    def validate(self, instance, value):
        """Validates the field."""
        super(DateTimeField, self).validate(instance, value)

        if not isinstance(value, datetime.datetime):
            instance.errors.add(self.name, "must be a valid date and time")

class FloatField(BaseField):
    """Represents a floating point number for a Mongo Document.

    Supports all the validations in *BaseField* and the following:

    min_value -- validates the minimum value the field value can be
    max_value -- validates the maximum value the field value can be

    """
    def __init__(self, name, min_value=None, max_value=None, **kwargs):
        super(FloatField, self).__init__(name, **kwargs)

        self.min_value = None if None == min_value else float(min_value)
        self.max_value = None if None == max_value else float(max_value)

    def validate(self, instance, value):
        """Validates the field."""
        super(FloatField, self).validate(instance, value)

        if isinstance(value, int):
            value = float(value)

        if not isinstance(value, float):
            instance.errors.add(self.name, "must be a float")

        if not None == self.min_value and value < self.min_value:
            instance.errors.add(self.name,
                "is too small (minimum is %s)" % self.min_value)

        if not None == self.max_value and value > self.max_value:
            instance.errors.add(self.name,
                "is too big (maximum is %s)" % self.max_value)

class IntegerField(BaseField):
    """Represents a integer number for a Mongo Document.

    Supports all the validations in *BaseField* and the following:

    min_value -- validates the minimum value the field value can be
    max_value -- validates the maximum value the field value can be

    """
    def __init__(self, name, min_value=None, max_value=None, **kwargs):
        super(IntegerField, self).__init__(name, **kwargs)

        self.min_value = None if None == min_value else int(min_value)
        self.max_value = None if None == max_value else int(max_value)

    def validate(self, instance, value):
        """Validates the field."""
        super(IntegerField, self).validate(instance, value)

        if not isinstance(value, int):
            instance.errors.add(self.name, "must be a integer")

        if not None == self.min_value and value < self.min_value:
            instance.errors.add(self.name,
                "is too small (minimum is %s)" % self.min_value)

        if not None == self.max_value and value > self.max_value:
            instance.errors.add(self.name,
                "is too big (maximum is %s)" % self.max_value)

class StringField(BaseField):
    """Represents a String field for a Mongo Document.

    Supports all the validations in *BaseField* and the following:

    length     -- validates the field value has an exact length; default is
                  *None*

    min_length -- ensures field has a minimum number of characters; default is
                  *None*

    max_length -- ensures field is not more than a maximum number of
                  characters; default is *None*

    pattern    -- validates the field matches the given regular expression
                  pattern; default is *None*

    """
    def __init__(self, name, length=None, min_length=None, max_length=None,
            pattern=None, **kwargs):
        super(StringField, self).__init__(name, **kwargs)

        self.length     = length
        self.min_length = min_length
        self.max_length = max_length
        self.regex      = re.compile(pattern) if pattern else None

    def validate(self, instance, value):
        """Validates the field."""
        super(StringField, self).validate(instance, value)
        val_length = len(value) if value else None

        if self.length and self.length != val_length:
            instance.errors.add(self.name,
                "is the wrong length (should be %s characters)" % self.length)

        if self.min_length and val_length < self.min_length:
            instance.errors.add(self.name,
                "is too short (minimum is %s characters)" % self.min_length)

        if self.max_length and val_length > self.max_length:
            instance.errors.add(self.name,
                "is too long (maximum is %s characters)" % self.max_length)

        if self.regex and self.regex.match(value) is None:
            instance.errors.add(self.name, "is in the wrong format")

class EmbeddedField(BaseField):
    """Represents an embedded Mongo document. Raises a TaviTypeError if *doc*
    is not a tavi.document.EmbeddedDocument.

    """
    def __init__(self, name, doc):
        super(EmbeddedField, self).__init__(name)
        doc_instance = doc()
        if not isinstance(doc_instance, EmbeddedDocument):
            raise TaviTypeError(
                "expected %s to be a subclass of "
                "tavi.document.EmbeddedDocument" %
                doc_instance.__class__
            )

        self.value = doc_instance

    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value):
        if value:
            for field in value.fields:
                embedded_value = getattr(value, field, None)
                setattr(self.value, field, embedded_value)

class ListField(BaseField):
    """Represents a list of embedded document fields."""
    def __get__(self, instance, owner):
        if self.attribute_name not in instance.__dict__:
            setattr(instance, self.attribute_name, EmbeddedList(self.name))
        return getattr(instance, self.attribute_name)

    def __set__(self, instance, value):
        pass
