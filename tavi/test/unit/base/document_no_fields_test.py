# -*- coding: utf-8 -*-
import unittest
from tavi.base.documents import BaseDocument


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
