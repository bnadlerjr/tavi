"""Utilities for JSON serialization. Relies on bson.json_util."""
from bson.json_util import dumps, loads

def serializable(cls):
    """Allows Document model objects to be (de)serialized from/to JSON."""
    class Wrapper(object):
        """Serialization decorator."""
        def __init__(self, **kwargs):
            self.wrapped = cls(**kwargs)

        def __getattr__(self, *args):
            return getattr(self.wrapped, *args)

        def to_json(self, fields=None):
            """Convert Document model object to JSON. Optionally, specify which
            fields should be serialized.

            """
            if fields:
                return dumps({ field: self.wrapped.data[field] for field in
                    fields })
            else:
                return dumps(self.wrapped.data)

        @staticmethod
        def from_json(json_str):
            """Deserialize a JSON string into a Document model object."""
            attrs = loads(json_str)
            return cls(**attrs)

    return Wrapper
