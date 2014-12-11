# -*- coding: utf-8 -*-
from integration import BaseMongoTest
from tavi.documents import Document, EmbeddedDocument
from tavi import fields


class Address(EmbeddedDocument):
    street = fields.StringField("street")
    city = fields.StringField("city")
    state = fields.StringField("state")
    postal_code = fields.StringField("postal_code")


class OrderLine(EmbeddedDocument):
    quantity = fields.IntegerField("quantity")
    total_price = fields.FloatField("total_price")
    created_at = fields.DateTimeField("created_at")
    last_modified_at = fields.DateTimeField("last_modified_at")


class Order(Document):
    name = fields.StringField("name")
    address = fields.EmbeddedField("address", Address)
    email = fields.StringField("email")
    pay_type = fields.StringField("pay_type")
    order_lines = fields.ListField("order_lines", OrderLine)


class OrderTest(BaseMongoTest):
    def test_initialize_with_attributes(self):
        order = Order(
            name="John Doe",
            email="jdoe@example.com",
            pay_type="Mastercard"
        )

        self.assertEqual("John Doe", order.name)
        self.assertEqual("jdoe@example.com", order.email)
        self.assertEqual("Mastercard", order.pay_type)

    def test_address_is_embedded_document(self):
        address = Address(
            street="123 Elm St.",
            city="Anywhere",
            state="NJ",
            postal_code="00000"
        )

        order = Order(address=address)

        self.assertEqual("123 Elm St.", order.address.street)
        self.assertEqual("Anywhere", order.address.city)
        self.assertEqual("NJ", order.address.state)
        self.assertEqual("00000", order.address.postal_code)

    def test_insert_with_address(self):
        order = Order(
            name="John Doe",
            email="jdoe@example.com",
            pay_type="Mastercard"
        )

        order.address = Address()
        order.address.street = "123 Elm St."
        order.address.city = "Anywhere"
        order.address.state = "NJ"
        order.address.postal_code = "00000"

        assert order.save(), order.errors.full_messages

        orders = list(self.db.orders.find())
        self.assertEqual(1, len(orders))

        self.assertEqual("123 Elm St.", orders[0]["address"]["street"])
        self.assertEqual("Anywhere", orders[0]["address"]["city"])
        self.assertEqual("NJ", orders[0]["address"]["state"])
        self.assertEqual("00000", orders[0]["address"]["postal_code"])

    def test_update_with_address(self):
        order = Order(
            name="John Doe",
            email="jdoe@example.com",
            pay_type="Mastercard"
        )

        order.address = Address()
        order.address.street = "123 Elm St."
        order.address.city = "Anywhere"
        order.address.state = "NJ"
        order.address.postal_code = "00000"

        assert order.save(), order.errors.full_messages
        order.address.street = "1313 Mockingbird Lane"
        assert order.save(), order.errors.full_messages

        orders = list(self.db.orders.find())
        self.assertEqual(1, len(orders))

        self.assertEqual(
            "1313 Mockingbird Lane",
            orders[0]["address"]["street"]
        )

    def test_insert_with_order_lines(self):
        order = Order(
            name="John Doe",
            email="jdoe@example.com",
            pay_type="Mastercard"
        )

        line_a = OrderLine(quantity=1, total_price=19.99)
        line_b = OrderLine(quantity=3, total_price=39.99)

        order.order_lines.append(line_a)
        order.order_lines.append(line_b)

        assert order.save(), order.errors.full_messages

        orders = list(self.db.orders.find())
        lines = orders[0]["order_lines"]
        self.assertEqual(1, len(orders))
        self.assertEqual(2, len(lines))

        self.assertEqual(1, lines[0]["quantity"])
        self.assertEqual(19.99, lines[0]["total_price"])
        self.assertIsNotNone(lines[0]["created_at"])
        self.assertEqual(lines[0]["created_at"], lines[0]["last_modified_at"])

        self.assertEqual(3, lines[1]["quantity"])
        self.assertEqual(39.99, lines[1]["total_price"])
        self.assertIsNotNone(lines[1]["created_at"])
        self.assertEqual(lines[1]["created_at"], lines[1]["last_modified_at"])

    def test_update_with_order_lines(self):
        order = Order(
            name="John Doe",
            email="jdoe@example.com",
            pay_type="Mastercard"
        )

        line_a = OrderLine(quantity=1, total_price=19.99)
        line_b = OrderLine(quantity=3, total_price=39.99)
        order.order_lines.append(line_a)
        order.order_lines.append(line_b)

        assert order.save(), order.errors.full_messages
        orders = list(self.db.orders.find())
        self.assertEqual(1, len(orders))
        self.assertEqual(2, len(orders[0]["order_lines"]))

        order.order_lines[0].quantity = 42
        assert order.save(), order.errors.full_messages

        orders = list(self.db.orders.find())
        lines = orders[0]["order_lines"]
        self.assertEqual(1, len(orders))
        self.assertEqual(2, len(lines))

        self.assertEqual(42, lines[0]["quantity"])
        self.assertEqual(19.99, lines[0]["total_price"])
        self.assertIsNotNone(lines[0]["created_at"])

        self.assertAlmostEqual(
            0,
            (lines[0]["created_at"] -
                lines[0]["last_modified_at"]).total_seconds(),
            delta=1
        )

        self.assertEqual(3, lines[1]["quantity"])
        self.assertEqual(39.99, lines[1]["total_price"])
        self.assertIsNotNone(lines[1]["created_at"])

        self.assertAlmostEqual(
            0,
            (lines[1]["created_at"] -
                lines[1]["last_modified_at"]).total_seconds(),
            delta=1
        )

    def test_query_order_lines(self):
        order = Order(
            name="John Doe",
            email="jdoe@example.com",
            pay_type="Mastercard"
        )

        line_a = OrderLine(quantity=1, total_price=19.99)
        line_b = OrderLine(quantity=3, total_price=39.99)
        order.order_lines.append(line_a)
        order.order_lines.append(line_b)

        assert order.save(), order.errors.full_messages

        db_orders = Order.find_all()
        self.assertEqual(1, len(db_orders))

        db_lines = db_orders[0].order_lines
        self.assertEqual(1, db_lines[0].quantity)
        self.assertEqual(19.99, db_lines[0].total_price)

    def test_update_with_multiple_order_lines(self):
        order = Order(
            name="John Doe",
            email="jdoe@example.com",
            pay_type="Mastercard"
        )

        line_a = OrderLine(quantity=1, total_price=19.99)
        line_b = OrderLine(quantity=3, total_price=39.99)
        order.order_lines.append(line_a)
        order.order_lines.append(line_b)

        assert order.save(), order.errors.full_messages
        orders = list(self.db.orders.find())
        self.assertEqual(1, len(orders))
        self.assertEqual(2, len(orders[0]["order_lines"]))

        order.order_lines[0].quantity = 42
        assert order.save(), order.errors.full_messages

        orders = list(self.db.orders.find())
        lines = orders[0]["order_lines"]
        self.assertEqual(1, len(orders))
        self.assertEqual(2, len(lines))

        self.assertEqual(42, lines[0]["quantity"])
        self.assertEqual(19.99, lines[0]["total_price"])
        self.assertNotEqual(
            lines[0]["created_at"],
            lines[0]["last_modified_at"]
        )

        self.assertEqual(3, lines[1]["quantity"])
        self.assertEqual(39.99, lines[1]["total_price"])
        self.assertNotEqual(
            lines[1]["created_at"],
            lines[1]["last_modified_at"]
        )
