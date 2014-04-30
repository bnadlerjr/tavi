# -*- coding: utf-8 -*-
"""Provides base field support."""


class BaseField(object):
    """Base class for Mongo Document fields.

    name -- the name of the document field

    All *BaseFields* support the following default validations:

    required  -- indicates if the field is required; default is *False*
    default   -- default value for the field; *None* if not given
    choices -- validates field value is a member of specified list
    persist   -- boolean indicating if field should be persisted to Mongo;
                 default is True

    """

    _creation_counter = 0

    def __init__(
        self, name,
        required=False, default=None, choices=None, persist=True, unique=False
    ):
        self.name = name
        self.attribute_name = "_%s" % name
        self.required = required
        self.default = default
        self.choices = choices
        self.persist = persist
        self.unique = unique
        self.creation_order = BaseField._creation_counter
        BaseField._creation_counter += 1

    def __get__(self, instance, owner):
        if self.attribute_name not in instance.__dict__ and self.default:
            self.__set__(instance, self.default)
        return getattr(instance, self.attribute_name)

    def __set__(self, instance, value):
        if None == value and self.required and self.default:
            value = self.default
        self.validate(instance, value)
        setattr(instance, self.attribute_name, value)
        if hasattr(instance, "changed_fields"):
            instance.changed_fields.add(self.name)

    def validate(self, instance, value):
        """Validates the field.

        Subclasses should call *super* and implement their own validation.
        Assumes that *obj* has an *errors* attribute that acts like a
        tavi.errors.Errors class.

        """
        instance.errors.clear(self.name)
        if self.required and None == value:
            instance.errors.add(self.name, "is required")

        if self.choices and value not in self.choices:
            instance.errors.add(self.name, "value must be in list")
