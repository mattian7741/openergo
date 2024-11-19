from io import StringIO
from openergo.utility import Utility  # Import the Utility class
import pytest


class TestStreamJsonObjects:
    def test_stream_invalid_json_throws_exception(self):
        """Test that invalid JSON throws an exception."""
        input_stream = StringIO('{"a": "B",')
        with pytest.raises(ValueError):
            list(Utility.json_stream_to_object(input_stream))

    def test_stream_unfinished_input_stream_throws_exception(self):
        """Test that an unfinished JSON input throws an exception."""
        input_stream = StringIO('{"c": "D"')
        with pytest.raises(ValueError):
            list(Utility.json_stream_to_object(input_stream))

    def test_stream_generator_input_stream(self):
        """Test that the function works with a generator producing the text stream."""
        def generate_input():
            yield '{"e": "F}"}'
            yield '{"g": "H]"}'
            yield '{"i{": "J"}'

        # Simulate a generator input
        generator = generate_input()
        combined_input = StringIO(''.join(generator))
        results = list(Utility.json_stream_to_object(combined_input))
        assert results == [{'e': 'F}'}, {'g': 'H]'}, {'i{': 'J'}]

    def test_stream_multiple_json_objects_without_commas_should_fail(self):
        """Test that multiple JSON objects without commas should fail."""
        input_stream = StringIO('{"k": "L]"}, {"m": "N"}, {"o": "P"}')
        with pytest.raises(ValueError):
            list(Utility.json_stream_to_object(input_stream))

    def test_stream_multiple_separated_json_objects(self):
        """Test that multiple separated JSON objects are parsed correctly."""
        input_stream = StringIO('{"q": "R"}        {"s}": "T"}                        {"u]": "V"}')
        results = list(Utility.json_stream_to_object(input_stream))
        assert results == [{'q': 'R'}, {'s}': 'T'}, {'u]': 'V'}]

    def test_stream_json_array_as_single_entity(self):
        """Test that a JSON array is returned as a single entity."""
        input_stream = StringIO('[{"w": "X}"}, {"y": "Z]"}, {"{Aa": "bB"}]')
        results = list(Utility.json_stream_to_object(input_stream))
        assert results == [[{'w': 'X}'}, {'y': 'Z]'}, {'{Aa': 'bB'}]]

    def test_text_invalid_json_throws_exception(self):
        """Test that invalid JSON throws an exception."""
        with pytest.raises(ValueError):
            list(Utility.json_text_to_object('{"a": "B",'))

    def test_text_unfinished_input_stream_throws_exception(self):
        """Test that an unfinished JSON input throws an exception."""
        with pytest.raises(ValueError):
            list(Utility.json_text_to_object('{"c": "D"'))

    def test_text_generator_input_stream(self):
        """Test that the function works with a generator producing the text stream."""
        def generate_input():
            yield '{"e": "F}"}'
            yield '{"g": "H]"}'
            yield '{"i{": "J"}'

        generator = generate_input()
        combined_input = ''.join(generator)
        results = list(Utility.json_text_to_object(combined_input))
        assert results == [{'e': 'F}'}, {'g': 'H]'}, {'i{': 'J'}]

    def test_text_multiple_json_objects_without_commas_should_fail(self):
        """Test that multiple JSON objects without commas should fail."""
        with pytest.raises(ValueError):
            list(Utility.json_text_to_object('{"k": "L]"}, {"m": "N"}, {"o": "P"}'))

    def test_text_multiple_separated_json_objects(self):
        """Test that multiple separated JSON objects are parsed correctly."""
        input_stream = '{"q": "R"}        {"s}": "T"}                        {"u]": "V"}'
        results = list(Utility.json_text_to_object(input_stream))
        assert results == [{'q': 'R'}, {'s}': 'T'}, {'u]': 'V'}]

    def test_text_json_array_as_single_entity(self):
        """Test that a JSON array is returned as a single entity."""
        input_stream = '[{"w": "X}"}, {"y": "Z]"}, {"{Aa": "bB"}]'
        results = list(Utility.json_text_to_object(input_stream))
        assert results == [[{'w': 'X}'}, {'y': 'Z]'}, {'{Aa': 'bB'}]]
