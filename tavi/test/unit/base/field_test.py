import unittest
from tavi.base.fields import BaseField
from tavi.errors import Errors

class BaseFieldTest(unittest.TestCase):
    def setUp(self):
        self.field = BaseField("my_field")

    def test_has_a_name(self):
        self.assertEqual("my_field", self.field.name)

    def test_sets_default_value_for_required_attribute(self):
        self.assertFalse(self.field.required, "expected required to be False")

    def test_sets_default_value_for_default_attribute(self):
        self.assertIsNone(self.field.default)

    def test_supports_required_attribute(self):
        class Target(object):
            f = BaseField("my_field", required=True)
            errors = Errors()

        t = Target()
        t.f = None
        self.assertEqual(["My Field is required"], t.errors.full_messages)

        t.f = 42
        self.assertEqual(0, t.errors.count)

    def test_supports_default_value(self):
        class Target(object):
            f = BaseField("my_field", default=1)
            errors = Errors()

        t = Target()
        self.assertEqual(1, t.f)
        t.f = 42
        self.assertEqual(42, t.f)

    def test_validates_inclusion(self):
        class Target(object):
            f = BaseField("my_field", inclusion=['type_a', 'type_b'])
            errors = Errors()

        t = Target()
        t.f = "not a choice"
        self.assertEqual(["My Field value must be in list"],
            t.errors.full_messages)

        t.f = "type_a"
        self.assertEqual(0, t.errors.count)

    def test_accepts_a_persist_keyword_argument(self):
        class Target(object):
            f = BaseField("my_field", persist=False)
            errors = Errors()

        t = Target()

    def test_multiple_fields_do_not_share_attributes(self):
        another_field = BaseField("another_field")
        self.assertEqual("my_field", self.field.name)
        self.assertEqual("another_field", another_field.name)

    def test_invalid_default_value_is_not_allowed(self):
        class TestField(BaseField):
            def validate(self, instance, value):
                super(TestField, self).validate(instance, value)
                if value == -1:
                    instance.errors.add(self.name, "value cannot be -1")

        class Target(object):
            f = TestField("afield", default=-1)
            errors = Errors()

        t = Target()

        # the default value for field f is -1 which is not a valid value.
        # what should happen when f is accessed before it is set?
        self.assertNotEqual(-1, t.f)
        self.assertEqual(1, t.errors.count)

