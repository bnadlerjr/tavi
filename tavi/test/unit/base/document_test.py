# -*- coding: utf-8 -*-
import unittest
from tavi.base.documents import BaseDocument
from tavi.documents import EmbeddedDocument
from tavi.fields import EmbeddedField, ListField, StringField, DateTimeField


class BaseDocumentNoFieldsTest(unittest.TestCase):
    class NoFieldsSample(BaseDocument):
        pass

    def setUp(self):
        super(BaseDocumentNoFieldsTest, self).setUp()
        self.no_fields_sample = self.NoFieldsSample()

    def test_get_fields(self):
        self.assertEqual([], self.no_fields_sample.fields)

    def test_get_errors(self):
        self.assertEqual(0, self.no_fields_sample.errors.count)

    def test_valid(self):
        self.assertEqual(True, self.no_fields_sample.valid)

    def test_get_field_values(self):
        self.assertEqual({}, self.no_fields_sample.field_values)


class BaseDocumentPropertiesTest(unittest.TestCase):
    class Sample(BaseDocument):
        name = StringField("name", required=True)
        password = StringField("password", persist=False)
        payment_type = StringField("payment_type")
        created_at = DateTimeField("created_at")
        status = StringField("my_status")

    class Address(EmbeddedDocument):
        street = StringField("street")
        city = StringField("city")

    def setUp(self):
        super(BaseDocumentPropertiesTest, self).setUp()
        self.sample = self.Sample()

    def test_get_fields(self):
        self.assertEqual(
            ["name", "payment_type", "created_at", "status"],
            self.sample.fields
        )

    def test_get_field_values(self):
        sample = self.Sample(name="John")
        self.assertEqual({
            "name": "John",
            "payment_type": None,
            "created_at": None,
            "status": None
        }, sample.field_values)

    def test_get_mongo_field_values(self):
        sample = self.Sample(name="John", status="active")
        self.assertEqual({
            "name": "John",
            "payment_type": None,
            "created_at": None,
            "my_status": "active"
        }, sample.mongo_field_values)

    def test_get_errors(self):
        self.sample.name = None
        self.assertEqual(
            ["Name is required"],
            self.sample.errors.full_messages
        )

    def test_valid_when_no_errors(self):
        self.sample.name = "test"
        self.assertTrue(self.sample.valid, "expected sample to be valid")

    def test_invalid_when_errors(self):
        self.sample.name = None
        self.assertFalse(self.sample.valid, "expected sample to be invalid")

    def test_get_field_values_with_embedded_field(self):
        class SampleWithEmbeddedField(BaseDocument):
            name = StringField("name", required=True)
            address = EmbeddedField("address", self.Address)

        sample = SampleWithEmbeddedField(name="John")
        sample.address = self.Address()
        sample.address.street = "123 Elm St."
        sample.address.city = "Anywhere"

        self.assertEqual({
            "name": "John",
            "address": {
                "street": "123 Elm St.",
                "city": "Anywhere"
            }}, sample.field_values)

    def test_get_field_values_with_embedded_list_field(self):
        class SampleWithEmbeddedListField(BaseDocument):
            addresses = ListField("addresses", self.Address)

        sample = SampleWithEmbeddedListField()
        address = self.Address(street="123 Elm Street", city="Anywhere")

        sample.addresses.append(address)

        self.assertEqual({
            "addresses": [{
                "street": "123 Elm Street",
                "city": "Anywhere"
            }]}, sample.field_values)


class BaseDocumentInitializationTest(unittest.TestCase):
    class Sample(BaseDocument):
        name = StringField("name", required=True)
        password = StringField("password", persist=False)
        payment_type = StringField("payment_type")
        created_at = DateTimeField("created_at")

    def setUp(self):
        super(BaseDocumentInitializationTest, self).setUp()
        self.sample = self.Sample()

    def test_init_with_kwargs(self):
        sample = self.Sample(name="John")
        self.assertEqual("John", sample.name)

    def test_init_ignore_non_field_kwargs(self):
        sample = self.Sample(name="John", not_a_field=True)
        self.assertEqual("John", sample.name)

    def test_init_with_kwargs_does_not_overwrite_attributes(self):
        class User(BaseDocument):
            first_name = StringField("first_name")
            last_name = StringField("last_name")

        user_a = User(first_name="John", last_name="Doe")
        user_b = User(first_name="Walter", last_name="White")

        self.assertEqual("John", user_a.first_name)
        self.assertEqual("Doe", user_a.last_name)

        self.assertEqual("Walter", user_b.first_name)
        self.assertEqual("White", user_b.last_name)

    def test_init_multiple_does_not_overwrite_attributes(self):
        class User(BaseDocument):
            first_name = StringField("first_name")
            last_name = StringField("last_name")

        user_a = User()
        user_a.first_name = "John"
        user_a.last_name = "Doe"

        user_b = User()
        user_b.first_name = "Walter"
        user_b.last_name = "White"

        self.assertEqual("John", user_a.first_name)
        self.assertEqual("Doe", user_a.last_name)

        self.assertEqual("Walter", user_b.first_name)
        self.assertEqual("White", user_b.last_name)
