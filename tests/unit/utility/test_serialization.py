from openergo.utility import Utility  # Import the Utility class


class TestSerialization:
    def test_serialize_simple_data(self):
        """Test serialization of simple data types."""
        data = {'int': 42, 'str': 'hello', 'bool': True}
        serialized = Utility.serialize(data)  # Call the static method from Utility
        assert isinstance(serialized, str)

    def test_deserialize_simple_data(self):
        """Test deserialization of simple data types."""
        data = {'int': 42, 'str': 'hello', 'bool': True}
        serialized = Utility.serialize(data)
        deserialized = Utility.deserialize(serialized)  # Call the static method from Utility
        assert deserialized == data

    def test_serialize_deserialize_complex_object(self):
        """Test serialization and deserialization of complex objects."""
        data = {'list': [1, 2, 3], 'dict': {'key': 'value'}}
        serialized = Utility.serialize(data)
        deserialized = Utility.deserialize(serialized)  # Call the static method from Utility
        assert deserialized == data
