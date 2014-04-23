# -*- coding: utf-8 -*-
import unittest
from tavi.documents import EmbeddedDocument
from tavi import fields


class EmbeddedDocumentTest(unittest.TestCase):
    class Sample(EmbeddedDocument):
        first_name = fields.StringField("first_name")
        last_name = fields.StringField("last_name")

    def test_equal_if_all_attributes_equal(self):
        sample_a = self.Sample(
            first_name="John",
            last_name="Doe"
        )

        sample_b = self.Sample(
            first_name="John",
            last_name="Doe"
        )

        self.assertTrue(sample_a == sample_b)
        self.assertTrue(sample_b == sample_a)

    def test_unequal_if_attributes_are_not_equal(self):
        sample_a = self.Sample(
            first_name="John",
            last_name="Doe"
        )

        sample_b = self.Sample(
            first_name="James",
            last_name="Doe"
        )

        self.assertFalse(sample_a == sample_b)
        self.assertFalse(sample_b == sample_a)

    def test_unequal_if_not_exact_same_type(self):
        class AnotherSample(self.Sample):
            pass

        sample_a = self.Sample(
            first_name="John",
            last_name="Doe"
        )

        sample_b = AnotherSample(
            first_name="John",
            last_name="Doe"
        )

        self.assertFalse(sample_a == sample_b)
        self.assertFalse(sample_b == sample_a)

    def test_unequal_if_one_is_none(self):
        self.assertFalse(self.Sample is None)
