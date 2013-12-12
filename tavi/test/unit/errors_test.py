import unittest
from tavi.errors import Errors


class ErrorsTest(unittest.TestCase):
    def setUp(self):
        super(ErrorsTest, self).setUp()
        self.errors = Errors()

    def test_add_error(self):
        self.errors.add("email", "is required")
        self.assertEqual(["is required"], self.errors.get("email"))

    def test_add_errors_to_one_field(self):
        self.errors.add("email", "is required")
        self.errors.add("email", "must be valid")
        self.assertEqual(
            ["is required", "must be valid"],
            self.errors.get("email")
        )

    def test_clear(self):
        self.errors.add("email", "is required")
        self.errors.add("email", "must be valid")

        self.errors.clear("email")
        self.assertEqual(0, len(self.errors.get("email")))

    def test_count(self):
        self.errors.add("email", "is required")
        self.errors.add("email", "must be valid")
        self.errors.add("first_name", "is required")
        self.assertEqual(3, self.errors.count)

    def test_full_messages_for(self):
        self.errors.add("email", "is required")
        self.errors.add("email", "must be valid")
        self.errors.add("first_name", "is required")

        expected = [
            "Email is required",
            "Email must be valid"
        ]

        self.assertEqual(expected, self.errors.full_messages_for("email"))

    def test_full_messages(self):
        self.errors.add("email", "is required")
        self.errors.add("email", "must be valid")
        self.errors.add("first_name", "is required")

        self.assertTrue("Email is required" in self.errors.full_messages)
        self.assertTrue("Email must be valid" in self.errors.full_messages)
        self.assertTrue("First Name is required" in self.errors.full_messages)
