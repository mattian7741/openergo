from openergo.utility import Utility  # Import the Utility class


class TestDecorators:
    def test_traverse_single_elements(self):
        """Test traverse_datastructures on single and basic structures."""

        @Utility.traverse_datastructures
        def increment(x):
            if isinstance(x, (int, float)):  # Increment numeric types
                return x + 1
            return x  # Return as-is for non-numeric types

        assert increment(3) == 4
        assert increment([1, 2, 3]) == [2, 3, 4]
        assert increment((1, 2)) == (2, 3)
        assert increment({'a': 1, 'b': 2}) == {'a': 2, 'b': 3}

    def test_traverse_nested_structures(self):
        """Test traverse_datastructures on nested structures."""

        @Utility.traverse_datastructures
        def increment(x):
            if isinstance(x, (int, float)):  # Increment numeric types
                return x + 1
            return x  # Return as-is for non-numeric types

        nested_dict = {'a': 1, 'b': {'c': 2, 'd': [3, 4]}}
        assert increment(nested_dict) == {'a': 2, 'b': {'c': 3, 'd': [4, 5]}}

    def test_traverse_empty_structures(self):
        """Test traverse_datastructures on empty structures."""

        @Utility.traverse_datastructures
        def increment(x):
            if isinstance(x, (int, float)):  # Increment numeric types
                return x + 1
            return x  # Return as-is for non-numeric types

        assert increment([]) == []
        assert increment({}) == {}
        assert increment(()) == ()

    def test_root_node_basic_functionality(self):
        """Test root_node decorator with basic functionality."""

        @Utility.root_node
        def access_path(data, path):
            for part in path.strip().split('.'):
                if not isinstance(data, dict):  # Check if data is a dictionary
                    return data
                data = data.get(part, {})
            return data

        assert access_path(10, 'key') == 10
        assert access_path({'a': 1}, 'a') == 1

    def test_root_node_with_empty_key(self):
        """Test root_node decorator when the key is empty."""

        @Utility.root_node
        def access_path(data, path):
            for part in path.strip().split('.'):
                if not isinstance(data, dict):  # Check if data is a dictionary
                    return data
                data = data.get(part, {})
            return data

        assert access_path({'a': 1}, '') == {'a': 1}
