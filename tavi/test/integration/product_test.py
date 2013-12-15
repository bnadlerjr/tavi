# -*- coding: utf-8 -*-
import unittest
from integration import BaseMongoTest
from tavi import fields
from tavi.documents import Document


class Product(Document):
    name = fields.StringField("name", required=True)
    sku = fields.StringField("sku", required=True)
    description = fields.StringField("description", required=True)
    price = fields.FloatField("price", min_value=0)


class ProductTest(unittest.TestCase):
    def test_initialize(self):
        self.assertIsNotNone(Product())

    def test_initialize_with_attributes(self):
        p = Product(
            name="Macbook",
            sku="abc123",
            description="A laptop.",
            price=1499.99
        )

        self.assertEqual("Macbook", p.name)
        self.assertEqual("abc123", p.sku)
        self.assertEqual("A laptop.", p.description)
        self.assertEqual(1499.99, p.price)


class ProductValidationTest(unittest.TestCase):
    def setUp(self):
        super(ProductValidationTest, self).setUp()
        self.product = Product(
            name="Macbook",
            sku="abc123",
            description="A laptop.",
            price=1499.99
        )

    def test_does_not_have_errors_when_all_validations_are_met(self):
        self.assertTrue(self.product.valid, "expected product to be valid")
        self.assertEqual([], self.product.errors.full_messages)

    def test_is_invalid_without_name(self):
        self.assertTrue(self.product.valid, "expected product to be valid")
        self.product.name = None
        self.assertFalse(self.product.valid, "expected product to be invalid")
        self.assertEqual(
            ['Name is required'],
            self.product.errors.full_messages
        )

    def test_is_invalid_without_sku(self):
        self.assertTrue(self.product.valid, "expected product to be valid")
        self.product.sku = None
        self.assertFalse(self.product.valid, "expected product to be invalid")
        self.assertEqual(
            ['Sku is required'],
            self.product.errors.full_messages
        )

    def test_is_invalid_without_description(self):
        self.assertTrue(self.product.valid, "expected product to be valid")
        self.product.description = None
        self.assertFalse(self.product.valid, "expected product to be invalid")
        self.assertEqual(
            ['Description is required'],
            self.product.errors.full_messages
        )

    def test_is_invalid_if_price_is_not_a_number(self):
        self.assertTrue(self.product.valid, "expected product to be valid")
        self.product.price = "Not a number"
        self.assertEqual(
            ['Price must be a float'],
            self.product.errors.full_messages
        )
        self.assertFalse(self.product.valid, "expected product to be invalid")

    def test_is_invalid_if_price_is_less_than_zero(self):
        self.assertTrue(self.product.valid, "expected product to be valid")
        self.product.price = -1
        self.assertEqual(
            ['Price is too small (minimum is 0.0)'],
            self.product.errors.full_messages
        )
        self.assertFalse(self.product.valid, "expected product to be invalid")


class ProductPersistenceTest(BaseMongoTest):
    def setUp(self):
        super(ProductPersistenceTest, self).setUp()
        self.product = Product(
            name="Macbook",
            sku="abc123",
            description="A laptop.",
            price=1499.99
        )

    def test_inserts_a_new_product(self):
        self.product.save()
        self.assertIsNotNone(self.product.bson_id)

        products = list(self.db.products.find())
        self.assertEqual(1, len(products))

        self.assertEqual("Macbook", products[0]["name"])
        self.assertEqual("abc123", products[0]["sku"])
        self.assertEqual("A laptop.", products[0]["description"])
        self.assertEqual(1499.99, products[0]["price"])

    def test_update_a_product(self):
        self.product.save()
        self.product.name = "Macbook Pro"
        self.product.save()

        products = list(self.db.products.find())
        self.assertEqual(1, len(products))
        self.assertEqual("Macbook Pro", products[0]["name"])

    def test_cannot_save_if_product_invalid(self):
        self.product.description = None
        self.product.save()

        self.assertIsNone(self.product.bson_id)
        self.assertEqual(0, self.db.products.count())

    def test_delete_a_product(self):
        self.product.save()
        self.assertEqual(1, self.db.products.count())

        self.product.delete()
        self.assertEqual(0, self.db.products.count())
