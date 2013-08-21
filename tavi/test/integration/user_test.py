import unittest
from integration import BaseMongoTest
from tavi import fields
from tavi.document import Document

class User(Document):
    email      = fields.StringField("email",      required=True)
    first_name = fields.StringField("first_name", required=True)
    last_name  = fields.StringField("last_name",  required=True)

    @classmethod
    def find_by_email(cls, email):
        return cls.find_one({ "email": email })

    @classmethod
    def find_by_first_name(cls, first_name):
        return cls.find({ "first_name": first_name })

class UserTest(unittest.TestCase):
    def setUp(self):
        super(UserTest, self).setUp()
        self.user = User(
            email      = "jdoe@example.com",
            first_name = "John",
            last_name  = "Doe"
        )

    def test_initialize(self):
        self.assertIsNotNone(User())

    def test_initialize_with_fields(self):
        self.assertEqual("jdoe@example.com", self.user.email)
        self.assertEqual("John", self.user.first_name)
        self.assertEqual("Doe", self.user.last_name)

    def test_list_fields(self):
        self.assertEqual(['first_name', 'last_name', 'email'], self.user.fields)

class UserValidationTest(unittest.TestCase):
    def setUp(self):
        super(UserValidationTest, self).setUp()
        self.user = User(
            email      = "jdoe@example.com",
            first_name = "John",
            last_name  = "Doe"
        )

    def test_does_not_have_errors_when_all_validations_are_met(self):
        self.assertTrue(self.user.valid,
            "expected user to be valid (%s)" % self.user.errors.full_messages)
        self.assertEqual([], self.user.errors.full_messages)

    def test_is_invalid_without_email(self):
        self.assertTrue(self.user.valid,
            "expected user to be valid (%s)" % self.user.errors.full_messages)
        self.user.email = None
        self.assertFalse(self.user.valid, "expected user to be invalid")
        self.assertEqual(['Email is required'], self.user.errors.full_messages)

    def test_is_invalid_without_first_name(self):
        self.assertTrue(self.user.valid,
            "expected user to be valid (%s)" % self.user.errors.full_messages)
        self.user.first_name = None
        self.assertFalse(self.user.valid, "expected user to be invalid")
        self.assertEqual(['First Name is required'], self.user.errors.full_messages)

    def test_is_invalid_without_last_name(self):
        self.assertTrue(self.user.valid,
            "expected user to be valid (%s)" % self.user.errors.full_messages)
        self.user.last_name = None
        self.assertFalse(self.user.valid, "expected user to be invalid")
        self.assertEqual(['Last Name is required'], self.user.errors.full_messages)

    def test_is_invalid_with_multiple_errors(self):
        self.assertTrue(self.user.valid,
            "expected user to be valid (%s)" % self.user.errors.full_messages)
        self.user.first_name = None
        self.user.last_name = None
        self.assertFalse(self.user.valid, "expected user to be invalid")
        self.assertEqual([
            'First Name is required',
            'Last Name is required'
        ], self.user.errors.full_messages)

    def test_errors_are_reset_when_valid_is_called(self):
        self.assertTrue(self.user.valid,
            "expected user to be valid (%s)" % self.user.errors.full_messages)
        self.user.email = None
        self.user.first_name = None
        self.assertFalse(self.user.valid, "expected user to be invalid")

        self.user.email = "jdoe@example.com"

        self.assertFalse(self.user.valid, "expected user to be invalid")
        self.assertEqual(['First Name is required'], self.user.errors.full_messages)

class UserPersistenceTest(BaseMongoTest):
    def setUp(self):
        super(UserPersistenceTest, self).setUp()
        self.user = User(
            email      = "jdoe@example.com",
            first_name = "John",
            last_name  = "Doe"
        )

    def test_inserts_a_new_user(self):
        self.user.save()
        self.assertIsNotNone(self.user.bson_id)

        users = list(self.db.users.find())
        self.assertEqual(1, len(users))

        self.assertEqual("jdoe@example.com", users[0]["email"])
        self.assertEqual("John", users[0]["first_name"])
        self.assertEqual("Doe", users[0]["last_name"])

    def test_update_a_user(self):
        self.user.save()
        self.user.first_name = "Homer"
        self.user.save()

        users = list(self.db.users.find())
        self.assertEqual(1, len(users))
        self.assertEqual("Homer", users[0]['first_name'])

    def test_cannot_save_if_user_invalid(self):
        self.user.email = None
        self.user.save()

        self.assertIsNone(self.user.bson_id)
        self.assertEqual(0, self.db.users.count())

    def test_delete_a_user(self):
        self.user.save()
        self.assertEqual(1, self.db.users.count())

        self.user.delete()
        self.assertEqual(0, self.db.users.count())

class UserQueryTest(BaseMongoTest):
    def setUp(self):
        super(UserQueryTest, self).setUp()

        self.jdoe_id, self.jsmith_id, self.hsimpson_id = self.db.users.insert([
            {
                "email": "jdoe@example.com",
                "first_name": "John",
                "last_name": "Doe"
            },
            {
                "email": "jsmith@example.com",
                "first_name": "John",
                "last_name": "Smith"
            },
            {
                "email": "hsimpson@example.com",
                "first_name": "Homer",
                "last_name": "Simpson"
            }
        ])

    def test_find_by_object_id(self):
        user = User.find_by_id(self.jdoe_id)

        self.assertTrue(user.valid, "expected user to be valid")
        self.assertEqual("jdoe@example.com", user.email)
        self.assertEqual("John", user.first_name)
        self.assertEqual("Doe", user.last_name)

    def test_find_by_email(self):
        user = User.find_by_email("jdoe@example.com")

        self.assertTrue(user.valid, "expected user to be valid")
        self.assertEqual("jdoe@example.com", user.email)
        self.assertEqual("John", user.first_name)
        self.assertEqual("Doe", user.last_name)
