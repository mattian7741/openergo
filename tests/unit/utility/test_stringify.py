from openergo.utility import Utility  # Import the Utility class


class TestStringifyObjectify:
    def test_inverse_relationship(self):
        """Test that objectifying a stringified object returns the original object."""
        test_cases = [
            {"key": "value", "number": 42, "nested": {"inner_key": "inner_value"}},
            ["list", "of", "values", 123, 45.6, True, None],
            "simple string",
            12345,
            67.89,
            True,
            None,  # Added None explicitly
        ]

        for obj in test_cases:
            stringified = Utility.stringify(obj)  # Use Utility
            result = Utility.objectify(stringified)  # Use Utility
            assert result == obj, f"Failed for object: {obj}"

    def test_stringify_objectify_idempotency(self):
        """Test that stringify and objectify are idempotent."""
        json_strings = [
            '{"key": "value", "number": 42, "nested": {"inner_key": "inner_value"}}',
            '["list", "of", "values", 123, 45.6, true, null]',
            '"simple string"',
            "12345",
            "67.89",
            "true",
            "null",  # Added null explicitly
        ]

        for stringified in json_strings:
            obj = Utility.objectify(stringified)  # Use Utility
            result = Utility.stringify(obj)  # Use Utility
            assert result == stringified, f"Failed for string: {stringified}"
