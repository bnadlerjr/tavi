"""Provides base field support."""

class BaseField(object):
    """Base class for Mongo Document fields.

    name -- the name of the document field

    All *BaseFields* support the following default validations:

    required -- indicates if the field is required; default is *False*
    default  -- default value for the field; *None* if not given

    """
    def __init__(self, name, required=False, default=None):
        self.name = name
        self.attribute_name = "_%s" % name
        self.required = required
        self.default = default

    def __get__(self, instance, owner):
        if self.attribute_name not in instance.__dict__ and self.default:
            setattr(instance, self.attribute_name, self.default)
        return getattr(instance, self.attribute_name)

    def __set__(self, instance, value):
        self.validate(instance, value)
        setattr(instance, self.attribute_name, value)

    def validate(self, instance, value):
        """Validates the field.

        Subclasses should call *super* and implement their own validation.
        Assumes that *obj* has an *errors* attribute that acts like a
        tavi.errors.Errors class.

        """
        instance.errors.clear(self.name)
        if self.required and None == value:
            instance.errors.add(self.name, "is required")
