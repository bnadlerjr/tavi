import unittest
from bson import ObjectId
from datetime import datetime
from tavi import fields
from tavi.documents import Document, EmbeddedDocument
from tavi.errors import TaviTypeError, Errors

class BooleanFieldTest(unittest.TestCase):
    def test_validates_is_boolean(self):
        class Target(object):
            f = fields.BooleanField("my_boolean")
            errors = Errors()

        t = Target()
        t.f = True
        self.assertEqual(0, t.errors.count)

        t.f = None
        self.assertEqual(["My Boolean must be a valid boolean"],
            t.errors.full_messages)

        t.f = False
        self.assertEqual(0, t.errors.count)

class DateTimeFieldTest(unittest.TestCase):
    def test_validates_is_datetime(self):
        class Target(object):
            f = fields.DateTimeField("my_datetime")
            errors = Errors()

        t = Target()
        t.f = "not a datetime"
        self.assertEqual(["My Datetime must be a valid date and time"],
            t.errors.full_messages)

        t.f = datetime.utcnow()
        self.assertEqual(0, t.errors.count)

    def test_validates_if_not_required(self):
        class Target(object):
            f = fields.DateTimeField("my_datetime")
            errors = Errors()

        t = Target()
        t.f = None
        self.assertEqual(0, t.errors.count)

    def test_validates_base_errors(self):
        class Target(object):
            f = fields.DateTimeField("my_datetime", required=True)
            errors = Errors()

        t = Target()
        t.f = None
        self.assertEqual(["My Datetime is required"], t.errors.full_messages)

class FloatFieldTest(unittest.TestCase):
    def test_validates_is_float(self):
        class Target(object):
            f = fields.FloatField("my_float")
            errors = Errors()

        t = Target()
        t.f = "not a float"
        self.assertEqual(["My Float must be a float"], t.errors.full_messages)
        t.f = 2.2
        self.assertEqual(0, t.errors.count)

    def test_converts_an_int_to_float_when_validating(self):
        class Target(object):
            f = fields.FloatField("my_float")
            errors = Errors()

        t = Target()
        t.f = 4
        self.assertEqual(0, t.errors.count)
        self.assertEqual(4.0, t.f)

    def test_sets_default_min_value(self):
        f = fields.FloatField("my_float")
        self.assertEqual(None, f.min_value)

    def test_validates_min_value(self):
        class Target(object):
            f = fields.FloatField("my_float", min_value=5)
            errors = Errors()

        t = Target()
        t.f = 4.99
        self.assertEqual(["My Float is too small (minimum is 5.0)"],
            t.errors.full_messages)

        t.f = 5
        self.assertEqual(0, t.errors.count)

    def test_validates_min_value_of_zero(self):
        class Target(object):
            f = fields.FloatField("my_float", min_value=0)
            errors = Errors()

        t = Target()
        t.f = -4.99
        self.assertEqual(["My Float is too small (minimum is 0.0)"],
            t.errors.full_messages)

        t.f = 5
        self.assertEqual(0, t.errors.count)

    def test_sets_default_max_value(self):
        f = fields.FloatField("my_float")
        self.assertEqual(None, f.max_value)

    def test_validates_max_value(self):
        class Target(object):
            f = fields.FloatField("my_float", max_value=10)
            errors = Errors()

        t = Target()
        t.f = 10.00001
        self.assertEqual(["My Float is too big (maximum is 10.0)"],
            t.errors.full_messages)

        t.f = 10
        self.assertEqual(0, t.errors.count)

    def test_validates_max_value_if_zero(self):
        class Target(object):
            f = fields.FloatField("my_float", max_value=0)
            errors = Errors()

        t = Target()
        t.f = 10.00001
        self.assertEqual(["My Float is too big (maximum is 0.0)"],
            t.errors.full_messages)

        t.f = -10
        self.assertEqual(0, t.errors.count)

    def test_validates_base_errors(self):
        class Target(object):
            f = fields.FloatField("my_float", required=True, min_value=10)
            errors = Errors()

        t = Target()
        t.f = None
        self.assertEqual([
            "My Float is required",
            "My Float must be a float",
            "My Float is too small (minimum is 10.0)"],
            t.errors.full_messages
        )

class IntegerFieldTest(unittest.TestCase):
    def test_validates_is_integer(self):
        class Target(object):
            f = fields.IntegerField("my_integer")
            errors = Errors()

        t = Target()
        t.f = 2.2
        self.assertEqual(["My Integer must be a integer"], t.errors.full_messages)
        t.f = 2
        self.assertEqual(0, t.errors.count)

    def test_sets_default_min_value(self):
        f = fields.IntegerField("my_integer")
        self.assertEqual(None, f.min_value)

    def test_validates_min_value(self):
        class Target(object):
            f = fields.IntegerField("my_integer", min_value=5)
            errors = Errors()

        t = Target()
        t.f = 4
        self.assertEqual(["My Integer is too small (minimum is 5)"],
            t.errors.full_messages)

        t.f = 5
        self.assertEqual(0, t.errors.count)

    def test_validates_min_value_of_zero(self):
        class Target(object):
            f = fields.IntegerField("my_integer", min_value=0)
            errors = Errors()

        t = Target()
        t.f = -4
        self.assertEqual(["My Integer is too small (minimum is 0)"],
            t.errors.full_messages)

        t.f = 5
        self.assertEqual(0, t.errors.count)

    def test_sets_default_max_value(self):
        f = fields.IntegerField("my_integer")
        self.assertEqual(None, f.max_value)

    def test_validates_max_value(self):
        class Target(object):
            f = fields.IntegerField("my_integer", max_value=10)
            errors = Errors()

        t = Target()
        t.f = 11
        self.assertEqual(["My Integer is too big (maximum is 10)"],
            t.errors.full_messages)

        t.f = 10
        self.assertEqual(0, t.errors.count)

    def test_validates_max_value_if_zero(self):
        class Target(object):
            f = fields.IntegerField("my_integer", max_value=0)
            errors = Errors()

        t = Target()
        t.f = 10
        self.assertEqual(["My Integer is too big (maximum is 0)"],
            t.errors.full_messages)

        t.f = -10
        self.assertEqual(0, t.errors.count)

    def test_validates_base_errors(self):
        class Target(object):
            f = fields.IntegerField("my_integer", required=True, min_value=10)
            errors = Errors()

        t = Target()
        t.f = None
        self.assertEqual([
            "My Integer is required",
            "My Integer must be a integer",
            "My Integer is too small (minimum is 10)"],
            t.errors.full_messages
        )

class ObjectIdFieldTest(unittest.TestCase):
    def test_sets_and_gets_object_id(self):
        class Target(object):
            f = fields.ObjectIdField("my_field")
            errors = Errors()

        t, value = Target(), ObjectId()
        t.f = value
        self.assertEqual(value, t.f)

    def test_casts_value_as_object_id_if_string(self):
        class Target(object):
            f = fields.ObjectIdField("my_field")
            errors = Errors()

        t, value = Target(), ObjectId()
        t.f = str(value)
        self.assertEqual(value, t.f)

    def test_validates_is_object_id(self):
        class Target(object):
            f = fields.ObjectIdField("my_field")
            errors = Errors()

        t = Target()
        t.f = "not an object ID"
        self.assertEqual(["My Field must be a valid Object Id"],
            t.errors.full_messages)

class StringFieldTest(unittest.TestCase):
    def setUp(self):
        super(StringFieldTest, self).setUp()
        self.field = fields.StringField("my_field")

    def test_strips_whitespace_from_value(self):
        class Target(object):
            f = fields.StringField("my_field")
            errors = Errors()

        t = Target()
        t.f = ' a value with leading and trailing whitespace    '
        self.assertEqual('a value with leading and trailing whitespace', t.f)

    def test_sets_default_min_length(self):
        self.assertEqual(None, self.field.min_length)

    def test_validates_min_length(self):
        class Target(object):
            f = fields.StringField("my_field", min_length=10)
            errors = Errors()

        t = Target()
        t.f = "Not ten"
        self.assertEqual(["My Field is too short (minimum is 10 characters)"],
            t.errors.full_messages)

    def test_sets_default_max_length(self):
        self.assertEqual(None, self.field.max_length)

    def test_validates_max_length(self):
        class Target(object):
            f = fields.StringField("my_field", max_length=10)
            errors = Errors()

        t = Target()
        t.f = "More than ten characters"
        self.assertEqual(["My Field is too long (maximum is 10 characters)"],
            t.errors.full_messages)

    def test_sets_default_pattern(self):
        self.assertEqual(None, self.field.regex)

    def test_validates_pattern(self):
        class Target(object):
            f = fields.StringField("my_field", pattern="^This")
            errors = Errors()

        t = Target()
        t.f = "Does not match pattern"
        self.assertEqual(["My Field is in the wrong format"],
            t.errors.full_messages)

        t.f = "This is the right pattern"
        self.assertEqual(0, t.errors.count)

    def test_sets_default_exact_length(self):
        self.assertEqual(None, self.field.length)

    def test_validates_exact_length(self):
        class Target(object):
            f = fields.StringField("my_field", length=4)
            errors = Errors()

        t = Target()
        t.f = "more than four"
        self.assertEqual(
            ["My Field is the wrong length (should be 4 characters)"],
            t.errors.full_messages
        )

        t.f = "one"
        self.assertEqual(
            ["My Field is the wrong length (should be 4 characters)"],
            t.errors.full_messages
        )

        t.f = "four"
        self.assertEqual(0, t.errors.count)

    def test_validates_base_errors(self):
        class Target(object):
            f = fields.StringField("my_field", required=True, min_length=10)
            errors = Errors()

        t = Target()
        t.f = None
        self.assertEqual([
            "My Field is required",
            "My Field is too short (minimum is 10 characters)"],
            t.errors.full_messages
        )

    def test_handles_empty_strings_for_required_validation(self):
        class Target(object):
            f = fields.StringField("my_field", required=True, min_length=10)
            errors = Errors()

        t = Target()

        t.f = ''
        self.assertEqual([
            "My Field is required",
            "My Field is too short (minimum is 10 characters)"],
            t.errors.full_messages
        )

        t.f = '        '
        self.assertEqual([
            "My Field is required",
            "My Field is too short (minimum is 10 characters)"],
            t.errors.full_messages
        )

class EmbeddedFieldTest(unittest.TestCase):
    def test_must_be_an_embedded_document(self):
        class Address(object):
            pass
        class Target(object):
            errors = Errors()

        with self.assertRaises(TaviTypeError) as exc:
            Target.f = fields.EmbeddedField("address", Address)

        expected_msg = (
            "expected <class 'unit.fields_test.Address'> to be a subclass of "
            "tavi.document.EmbeddedDocument"
        )

        self.assertEqual(expected_msg, exc.exception.message)

    def test_assign_and_retrieve_values(self):
        class Address(EmbeddedDocument):
            pass
        class Target(object):
            f = fields.EmbeddedField("address", Address)
            errors = Errors()

        t = Target()
        t.f.street      = "123 Elm St."
        t.f.city        = "Anywhere"
        t.f.state       = "NJ"
        t.f.postal_code = "00000"

        self.assertEqual("123 Elm St.", t.f.street)
        self.assertEqual("Anywhere", t.f.city)
        self.assertEqual("NJ", t.f.state)
        self.assertEqual("00000", t.f.postal_code)

    def test_cannot_overwrite_class(self):
        class Address(EmbeddedDocument):
            pass
        class Other(EmbeddedDocument):
            pass
        class Target(object):
            f = fields.EmbeddedField("address", Address)
            errors = Errors()

        t = Target()
        t.f = Other()
        self.assertEqual(Address, t.f.__class__)

    def test_has_a_owner(self):
        class Address(EmbeddedDocument):
            pass
        class Target(Document):
            f = fields.EmbeddedField("address", Address)
            errors = Errors()

        t = Target()
        self.assertEqual(t, t.f.owner)


class ListFieldTest(unittest.TestCase):
    def test_sets_default_as_empty_list(self):
        class OrderLine(EmbeddedDocument):
            pass
        class Order(object):
            f = fields.ListField("orderlines")
            errors = Errors()

        order = Order()
        self.assertEqual([], order.f)

    def test_cannot_overwrite_value(self):
        class Other(object):
            pass
        class OrderLine(EmbeddedDocument):
            pass
        class Order(object):
            f = fields.ListField("orderlines")
            errors = Errors()

        order = Order()
        order.f = Other()
        self.assertEqual(fields.EmbeddedList, order.f.__class__)
