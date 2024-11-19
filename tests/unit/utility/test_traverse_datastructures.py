import pytest
from typing import Any, Dict, Optional
from openergo.executor import root_node, traverse_datastructures


# Example function for use with `traverse_datastructures`
def uppercase(value: Any) -> Any:
    if isinstance(value, str):
        return value.upper()
    return value


class TestDecorators:
    """Unit tests for `traverse_datastructures` and `root_node`."""

    def test_traverse_datastructures_with_dict(self):
        """Test `traverse_datastructures` with a dictionary."""
        @traverse_datastructures()
        def test_func(value: Any) -> Any:
            return uppercase(value)

        input_data = {"key1": "value1", "key2": {"nested_key": "nested_value"}}
        expected = {"KEY1": "VALUE1", "KEY2": {"NESTED_KEY": "NESTED_VALUE"}}
        assert test_func(input_data) == expected

    def test_traverse_datastructures_with_list(self):
        """Test `traverse_datastructures` with a list."""
        @traverse_datastructures()
        def test_func(value: Any) -> Any:
            return uppercase(value)

        input_data = ["item1", {"key": "value"}]
        expected = ["ITEM1", {"KEY": "VALUE"}]
        assert test_func(input_data) == expected

    def test_traverse_datastructures_with_tuple(self):
        """Test `traverse_datastructures` with a tuple."""
        @traverse_datastructures()
        def test_func(value: Any) -> Any:
            return uppercase(value)

        input_data = ("item1", {"key": "value"})
        expected = ("ITEM1", {"KEY": "VALUE"})
        assert test_func(input_data) == expected

    def test_traverse_datastructures_with_primitive(self):
        """Test `traverse_datastructures` with a primitive."""
        @traverse_datastructures()
        def test_func(value: Any) -> Any:
            return uppercase(value)

        input_data = "value"
        expected = "VALUE"
        assert test_func(input_data) == expected

    def test_root_node_with_dict(self):
        """Test `root_node` decorator with a dictionary."""
        @root_node()
        def test_func(data: Dict[str, Any]) -> Dict[str, Any]:
            return {"NESTED": data["__root__"]["value"]}

        input_data = {"value": "test"}
        expected = {"NESTED": "test"}
        assert test_func(input_data) == expected

    def test_root_node_with_list(self):
        """Test `root_node` decorator with a list."""
        @root_node()
        def test_func(data: Dict[str, Any]) -> Dict[str, Any]:
            return [item.upper() for item in data["__root__"]]

        input_data = ["value1", "value2"]
        expected = ["VALUE1", "VALUE2"]
        assert test_func(input_data) == expected

    def test_root_node_with_primitive(self):
        """Test `root_node` decorator with a primitive."""
        @root_node()
        def test_func(data: Dict[str, Any]) -> Dict[str, Any]:
            return data["__root__"].upper()

        input_data = "test"
        expected = "TEST"
        assert test_func(input_data) == expected

    def test_combined_decorators(self):
        """Test `root_node` and `traverse_datastructures` together."""
        @root_node(param_index=0)
        @traverse_datastructures(ignore=["__root__"])
        def test_func(value: Any) -> Any:
            return uppercase(value)

        input_data = {"value": "test", "nested": ["example", {"deep": "data"}]}
        expected = {"VALUE": "TEST", "NESTED": ["EXAMPLE", {"DEEP": "DATA"}]}
        assert test_func(input_data) == expected
