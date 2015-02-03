# -*- coding: utf-8 -*-
import unittest
from unit import LogCapture
from tavi.base.documents import BaseDocument
from tavi.documents import EmbeddedDocument
from tavi.fields import ListField, StringField
from tavi.fields import DateTimeField, FloatField


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
        with LogCapture() as log:
            sample = self.Sample(name="John", not_a_field=True)
            self.assertEqual("John", sample.name)

        msg = "Ignoring unknown field for Sample: 'not_a_field' = 'True'"
        self.assertEqual([msg], log.messages["debug"])

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

    def test_assign_to_list_field(self):
        class OrderLine(EmbeddedDocument):
            price = FloatField("price")

        class Order(BaseDocument):
            name = StringField("name")
            total = FloatField("total")
            order_lines = ListField("order_lines", OrderLine)

        order = Order()
        order_line = OrderLine(price=3.0)
        order.order_lines.append(order_line)

        self.assertEqual(3.0, order.order_lines[0].price)

    def test_init_with_embedded_list_args(self):
        class OrderLine(EmbeddedDocument):
            price = FloatField("price")

        class Order(BaseDocument):
            name = StringField("name")
            total = FloatField("total")
            order_lines = ListField("order_lines", OrderLine)

        order_hash = {
            "name": "foo",
            "total": 1.1,
            "order_lines": [{
                    "price": 2.1
            }]
        }
        order = Order(**order_hash)
        self.assertEqual("foo", order.name)
        self.assertEqual(2.1, order.order_lines[0].price)
