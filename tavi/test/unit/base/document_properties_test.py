# -*- coding: utf-8 -*-
import unittest
from tavi.base.documents import BaseDocument
from tavi.documents import EmbeddedDocument
from tavi.fields import EmbeddedField, ListField, StringField, DateTimeField


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


class BaseDocumentDirtyFieldCheckingTest(unittest.TestCase):
    class Sample(BaseDocument):
        name = StringField("name", required=True)
        password = StringField("password", persist=False)
        payment_type = StringField("payment_type")
        created_at = DateTimeField("created_at")
        status = StringField("my_status")

    def setUp(self):
        super(BaseDocumentDirtyFieldCheckingTest, self).setUp()
        self.sample = self.Sample()

    def test_field_are_not_dirty_when_initialized(self):
        self.assertEqual(0, len(self.sample.changed_fields))

    def test_field_is_added_to_changed_list_when_changed(self):
        self.sample.name = "my sample"
        self.assertEqual(set(["name"]), self.sample.changed_fields)

    def test_field_is_added_to_changed_list_only_once(self):
        self.sample.name = "my sample"
        self.assertEqual(set(["name"]), self.sample.changed_fields)
        self.sample.name = "changed name"
        self.assertEqual(set(["name"]), self.sample.changed_fields)
