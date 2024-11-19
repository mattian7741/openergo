from openergo.utility import Utility  # Import the Utility class


class TestSafeCast:
    def test_basic_type_casting(self):
        """Test safe casting of basic types."""
        assert Utility.safecast(int, "123") == 123
        assert Utility.safecast(float, "123.45") == 123.45
        assert Utility.safecast(str, 123) == "123"
        assert Utility.safecast(bool, "True") is True
        assert Utility.safecast(bool, "False") is False
        assert Utility.safecast(bool, "") is False
        assert Utility.safecast(bytes, "test") == b"test"

    def test_invalid_casting_attempts(self):
        """Test invalid type casting attempts that should raise TypeError."""
        import pytest

        with pytest.raises(TypeError):
            Utility.safecast(int, "not a number")
        with pytest.raises(TypeError):
            Utility.safecast(float, "not a float")
        with pytest.raises(TypeError):
            Utility.safecast(bool, 123)  # non-boolean to bool
        with pytest.raises(TypeError):
            Utility.safecast(tuple, "not an iterable")  # tuple casting with invalid iterable
        with pytest.raises(TypeError):
            Utility.safecast(dict, "not a dict")  # string to dict

    def test_collection_casting(self):
        """Test safe casting of collection types."""
        assert Utility.safecast(list, "123") == ['1', '2', '3']  # string to list of chars
        assert Utility.safecast(set, "123") == {'1', '2', '3'}  # string to set of unique chars
        assert Utility.safecast(tuple, [1, 2, 3]) == (1, 2, 3)  # list to tuple
        assert Utility.safecast(dict, [('a', 1), ('b', 2)]) == {'a': 1, 'b': 2}  # list of tuples to dict

        import pytest

        with pytest.raises(TypeError):
            Utility.safecast(list, 123)  # integer to list

    def test_edge_cases(self):
        """Test edge cases such as None, empty values, and unsupported types."""
        assert Utility.safecast(str, None) == "None"  # None to string
        assert Utility.safecast(int, "0") == 0  # zero value string to int
        assert Utility.safecast(float, "0.0") == 0.0  # zero value string to float

        import pytest

        with pytest.raises(TypeError):
            Utility.safecast(int, None)  # None to int should fail
        assert Utility.safecast(tuple, []) == ()  # empty list to tuple
        with pytest.raises(TypeError):
            Utility.safecast(tuple, None)  # None to tuple should fail
        with pytest.raises(TypeError):
            Utility.safecast(memoryview, "string")  # unsupported conversion

    def test_custom_types_and_hints(self):
        """Test casting with unsupported or custom types."""
        class CustomType:
            pass

        import pytest

        with pytest.raises(TypeError):
            Utility.safecast(CustomType, "test")  # unsupported custom type

        custom_instance = CustomType()
        assert str(custom_instance).startswith(
            f"<{custom_instance.__class__.__module__}.{custom_instance.__class__.__qualname__} object at"
        )
