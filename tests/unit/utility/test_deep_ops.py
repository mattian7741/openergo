import pytest  # Add this import
from openergo.utility import Utility  # Import the Utility class directly

_NO_VALUE = object()  # Using the same unique object for the sentinel


class TestDeepFunctions:
    def test_deep_get(self):
        data = {'a': {'b': {'c': 5}}}
        assert Utility.deep_get(data, 'a.b.c') == 5

        data = {'a': [{'b': 10}, {'c': 20}]}
        assert Utility.deep_get(data, 'a.1.c') == 20

        data = [{'a': {'b': [1, 2, 3]}}]
        assert Utility.deep_get(data, '0.a.b.2') == 3
        assert Utility.deep_get(data, 'x', default_sentinel=99) == 99

        with pytest.raises(KeyError):
            Utility.deep_get(data, 'z')

    def test_deep_set(self):
        data = {}
        Utility.deep_set(data, 'a.b.c', 5)
        assert data == {'a': {'b': {'c': 5}}}

        data = {'a': [1, 2]}
        Utility.deep_set(data, 'a.1', 3)
        assert data == {'a': [1, 3]}

        data = {'a': {'b': {'c': 5}}}
        Utility.deep_set(data, 'a.b.c', 10)
        assert data == {'a': {'b': {'c': 10}}}

    def test_deep_unset(self):
        # Removing existing key in a dictionary
        data = {'a': {'b': {'c': 5}}}
        Utility.deep_unset(data, 'a.b.c')
        assert data == {'a': {'b': {}}}  # Verify key is removed

        # Removing an item from a list inside a dictionary
        data = {'a': [{'b': 10}, {'c': 20}]}
        Utility.deep_unset(data, 'a.1')
        assert data == {'a': [{'b': 10}]}  # Verify item is removed from list

        # Test for handling non-existent key path
        data = {'a': {'b': {'c': 5}}}
        Utility.deep_unset(data, 'a.x.y')
        assert data == {'a': {'b': {'c': 5}}}  # Verify data remains unchanged because the key 'x' doesn't exist

        # Test for handling non-integer list index in key path
        data = {'a': [10, 20]}
        Utility.deep_unset(data, 'a.b')
        assert data == {'a': [10, 20]}  # Verify data remains unchanged because 'b' is not a valid index
