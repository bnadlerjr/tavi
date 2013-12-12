import unittest
from tavi import fields
from tavi.documents import Document, EmbeddedDocument
from tavi import EmbeddedList
from tavi.errors import TaviTypeError


class EmbeddedListTest(unittest.TestCase):
    class Address(EmbeddedDocument):
        street = fields.StringField("street", required=True)

    class Owner(Document):
        pass

    def setUp(self):
        super(EmbeddedListTest, self).setUp()
        self.my_list = EmbeddedList("addresses")
        self.owner = self.Owner()
        self.address1 = self.Address(street="123 Elm Street")
        self.address2 = self.Address(street="456 Pine Street")
        self.address3 = self.Address(street="789 Cedar Street")

    def test_has_a_name(self):
        self.assertEqual("addresses", self.my_list.name)

    def test_sets_default_owner(self):
        self.assertIsNone(self.my_list.owner)

    def test_owner_must_be_a_document(self):
        with self.assertRaises(TaviTypeError) as exc:
            self.my_list.owner = "not a document"

        self.assertEqual(
            "owner must be of type or inherit from "
            "tavi.base.document.BaseDocument",
            exc.exception.message
        )

    def test_add_single_item(self):
        self.my_list.append(self.address1)
        self.assertEqual([self.address1], self.my_list)

    def test_add_multiple_items(self):
        self.my_list.extend([self.address1, self.address2, self.address3])
        self.assertEqual(
            [self.address1, self.address2, self.address3],
            self.my_list
        )

    def test_sets_owner_of_added_item(self):
        self.my_list.owner = self.owner
        self.assertIsNone(self.address1.owner)
        self.my_list.append(self.address1)
        self.assertEqual(self.address1.owner, self.my_list.owner)

    def test_can_only_add_embedded_documents(self):
        with self.assertRaises(TaviTypeError) as exc:
            self.my_list.append(1)

        msg = (
            "tavi.EmbeddedList only accepts "
            "tavi.document.EmbeddedDocument objects"
        )

        self.assertEqual(msg, exc.exception.message)

    def test_cannot_add_invalid_items(self):
        self.my_list.owner = self.owner
        self.my_list.append(self.Address())
        self.assertEqual([], self.my_list)

    def test_merges_errors_with_owner(self):
        self.my_list.owner = self.owner
        self.my_list.append(self.Address())
        self.assertEqual(
            ["Addresses Error: Street is required"],
            self.owner.errors.full_messages
        )

    def test_find_item(self):
        self.my_list.append(self.address1)
        self.my_list.append(self.address2)
        self.my_list.append(self.address3)

        self.assertEqual(self.address2, self.my_list.find(self.address2))

    def test_cannot_find_item(self):
        self.my_list.append(self.address1)
        self.my_list.append(self.address2)
        self.my_list.append(self.address3)

        self.assertIsNone(self.my_list.find(self.Address()))

    def test_remove_item(self):
        self.my_list.append(self.address1)
        self.assertEqual([self.address1], self.my_list)

        self.my_list.remove(self.address1)
        self.assertEqual([], self.my_list)
