from openergo.utility import Utility  # Import the Utility class
import pytest


class TestUtilities:
    def test_unique_identifier(self):
        """Test that unique identifiers are indeed unique and correctly formatted."""
        id1 = Utility.unique_identifier("test")
        id2 = Utility.unique_identifier("test")
        assert id1 != id2
        assert id1.startswith("test_")

    def test_utc_string(self):
        """Test that UTC string is correctly formatted with prefix."""
        utc = Utility.utc_string("date")
        assert utc.startswith("date_")
        assert len(utc) == len("date_") + len("YYYYMMDDHHMMSSffffff")

    def test_uuid(self):
        """Test UUID generation is formatted correctly."""
        id = Utility.uuid("uuid")
        assert id.startswith("uuid_")
        assert len(id.split("_")[1]) == 36  # UUID is 36 characters long

    def test_hash(self):
        """Test hashing returns the correct format and consistent output."""
        result = Utility.hash("hello", "hash")
        assert result.startswith("hash_")
        assert Utility.hash("hello", "hash") == result

    def test_stringify(self):
        """Test conversion of objects to JSON string."""
        obj = {"key": "value", "num": 42}
        stringified = Utility.stringify(obj)
        assert stringified == '{"key": "value", "num": 42}'

    def test_objectify(self):
        """Test conversion from JSON string back to object."""
        string = '{"key": "value", "num": 42}'
        obj = Utility.objectify(string)
        assert obj == {"key": "value", "num": 42}

    def test_is_array(self):
        """Test array type checking."""
        assert Utility.is_array([1, 2, 3])
        assert Utility.is_array((1, 2, 3))
        assert not Utility.is_array({'a': 1})

    def test_safecast(self):
        """Test safe casting of types."""
        assert Utility.safecast(int, "123") == 123
        assert Utility.safecast(str, 123) == "123"
        with pytest.raises(TypeError):
            Utility.safecast(tuple, "not a tuple")
