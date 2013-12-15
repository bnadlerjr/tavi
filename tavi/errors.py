# -*- coding: utf-8 -*-
"""Defines custom errors."""
import inflection
from tavi.utils import flatten


class TaviError(Exception):
    """Base error for all Tavi errors."""
    pass


class TaviTypeError(TaviError):
    """Raised when an operation or function is applied to an object of
    inappropriate type.

    """
    pass


class TaviConnectionError(TaviError):
    """Raised when Tavi cannot connect to Mongo."""
    pass


class Errors(object):
    """Provides a dictionary-like object that is used for handing error
    messages for fields.

    """

    def __init__(self):
        self._errors = {}

    @property
    def count(self):
        """Returns the number of error messages."""
        return len(flatten(self._errors.values()))

    @property
    def full_messages(self):
        """Returns all the full error messages as a list."""
        return flatten(
            [self.full_messages_for(field) for field in self._errors]
        )

    def add(self, field, message):
        """Adds *message* to the error messages on *field*. More than one
        error can be added to the same *field*.

        """
        if field not in self._errors:
            self._errors[field] = []
        self._errors[field].append(message)

    def clear(self, field):
        """Clear the error messages."""
        self._errors[field] = []

    def full_messages_for(self, field):
        """Returns all the full error messages for a given *field* as a list.

        """
        humanized_field = inflection.titleize(inflection.humanize(field))
        return ["%s %s" % (humanized_field, msg) for msg in self.get(field)]

    def get(self, field):
        """Return error messages for *field*."""
        return self._errors[field]
