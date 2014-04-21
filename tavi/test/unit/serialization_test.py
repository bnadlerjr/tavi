# -*- coding: utf-8 -*-
import unittest
import datetime
from tavi import fields
from tavi.documents import Document


class SerializationTest(unittest.TestCase):
    class Target(Document):
        name = fields.StringField("name")
        price = fields.FloatField("price")
        quantity = fields.IntegerField("quantity")
        sold_on = fields.DateTimeField("sold_on")

    def test_serialize_to_json(self):
        t = self.Target(
            name="Widget",
            price=9.99,
            quantity=3,
            sold_on=datetime.datetime(2013, 8, 25, 22, 24, 0)
        )

        expected = (
            '{'
            '"id": null, '
            '"sold_on": {"$date": 1377469440000}, '
            '"price": 9.99, '
            '"name": "Widget", '
            '"quantity": 3'
            '}'
        )

        self.assertEqual(expected, t.to_json())

    def test_serialize_only_specified_fields_to_json(self):
        t = self.Target(
            name="Widget",
            price=9.99,
            quantity=3,
            sold_on=datetime.datetime(2013, 8, 25, 22, 24, 0)
        )

        expected = (
            '{'
            '"id": null, '
            '"price": 9.99, '
            '"name": "Widget", '
            '"quantity": 3'
            '}'
        )

        self.assertEqual(
            expected,
            t.to_json(fields=['bson_id', 'name', 'price', 'quantity'])
        )

    def test_deserialize_from_json(self):
        json = (
            '{'
            '"price": 9.99, '
            '"name": "Widget", '
            '"quantity": 3'
            '}'
        )

        t = self.Target.from_json(json)
        self.assertEqual(9.99, t.price)
        self.assertEqual("Widget", t.name)
        self.assertEqual(3, t.quantity)
