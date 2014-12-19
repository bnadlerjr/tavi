# -*- coding: utf-8 -*-
import unittest
from tavi.base.documents import BaseDocument
from tavi.fields import DateTimeField, StringField


class BaseDocumentModelValidationTest(unittest.TestCase):
    class Sample(BaseDocument):
        name = StringField("name", required=True)
        payment_type = StringField("payment_type")
        created_at = DateTimeField("created_at")
        status = StringField("my_status", choices=["Good", "Bad"])

        def __validate__(self):
            self.errors.clear("status")
            if self.payment_type and not self.status:
                self.errors.add("status", "is required if payment type is set")

    def setUp(self):
        super(BaseDocumentModelValidationTest, self).setUp()
        self.sample = self.Sample(name="John", payment_type="Debit")

    def test_pass_model_level_validation(self):
        self.sample.status = "Good"
        self.assertTrue(self.sample.valid, self.sample.errors.full_messages)
        self.assertEqual(0, self.sample.errors.count)

    def test_fail_model_level_validation(self):
        self.assertFalse(self.sample.valid)
        self.assertEqual([
            "Status is required if payment type is set",
            "My Status value must be in list"
            ], self.sample.errors.full_messages)

    def test_clears_model_level_errors(self):
        self.assertFalse(self.sample.valid)
        self.assertEqual([
            "Status is required if payment type is set",
            "My Status value must be in list"
            ], self.sample.errors.full_messages)

        self.sample.status = "Bad"
        self.assertTrue(self.sample.valid, self.sample.errors.full_messages)
        self.assertEqual(0, self.sample.errors.count)

    def test_clearing_model_validation_does_not_clear_field_validation(self):
        self.assertFalse(self.sample.valid)
        self.assertIn(
            "Status is required if payment type is set",
            self.sample.errors.full_messages
        )
        self.sample.status = "Not a valid status"
        self.assertFalse(self.sample.valid)
        self.assertEqual(
            ["My Status value must be in list"],
            self.sample.errors.full_messages
        )
