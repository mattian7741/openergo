import pytest
from typing import Any, Dict, Optional, List, Tuple
from openergo.executor import root_node, traverse_datastructures

def lowercase(value: Any) -> Any:
    if isinstance(value, str):
        return value.lower()
    return value

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




    def test_traverse_datastructures_ignore(self):
        """Test `traverse_datastructures` with an ignore list."""
        @traverse_datastructures(ignore=["ignore_this", "SKIP_ME"])
        def test_func(value: Any) -> Any:
            return lowercase(value)

        input_data = {
            "key1": "VALUE1",
            "ignore_this": "VALUE2",
            "nested": {"key2": "VALUE3", "SKIP_ME": "VALUE4"}
        }
        expected = {
            "key1": "value1",
            "ignore_this": "value2",
            "nested": {"key2": "value3", "SKIP_ME": "value4"}
        }
        assert test_func(input_data) == expected

    def test_traverse_datastructures_nested_structures(self):
        """Test `traverse_datastructures` with deeply nested mixed structures."""
        @traverse_datastructures()
        def test_func(value: Any) -> Any:
            return lowercase(value)

        input_data = {
            "key1": ["VALUE1", ("VALUE2", {"key2": "VALUE3"})],
            "key3": {"key4": ["VALUE4", {"key5": "VALUE5"}]}
        }
        expected = {
            "key1": ["value1", ("value2", {"key2": "value3"})],
            "key3": {"key4": ["value4", {"key5": "value5"}]}
        }
        assert test_func(input_data) == expected

    def test_traverse_datastructures_no_mutation(self):
        """Ensure `traverse_datastructures` does not mutate the original data."""
        @traverse_datastructures()
        def test_func(value: Any) -> Any:
            return lowercase(value)

        input_data = {"key1": "VALUE1", "key2": ["VALUE2", {"key3": "VALUE3"}]}
        original_copy = input_data.copy()
        _ = test_func(input_data)
        assert input_data == original_copy  # Ensure original data is unchanged

    def test_traverse_datastructures_empty_input(self):
        """Test `traverse_datastructures` with empty input."""
        @traverse_datastructures()
        def test_func(value: Any) -> Any:
            return lowercase(value)

        assert test_func({}) == {}
        assert test_func([]) == []
        assert test_func(()) == ()
        assert test_func(None) is None

    # -----------------------------
    # Tests for `root_node`
    # -----------------------------

    def test_root_node_with_nonzero_param_index(self):
        """Test `root_node` with a non-zero parameter index."""
        @root_node(param_index=1)
        def test_func(other_arg: Any, data: Dict[str, Any]) -> Any:
            return {"NESTED": data["__root__"]["value"]}

        input_data = {"value": "test"}
        other_arg = "irrelevant"
        expected = {"NESTED": "test"}
        assert test_func(other_arg, input_data) == expected

    def test_root_node_with_additional_parameters(self):
        """Test `root_node` decorator with additional non-root parameters."""
        @root_node(param_index=0)  # Wrap the first argument as the root node
        def test_func(data: Dict[str, Any], extra: str) -> str:
            return f"Root: {data['__root__']['key']}, Extra: {extra.upper()}"

        input_data = {"key": "value"}
        extra_arg = "test"
        expected = "Root: value, Extra: TEST"
        assert test_func(input_data, extra=extra_arg) == expected

    def test_root_node_with_empty_input(self):
        """Test `root_node` with empty input."""
        @root_node()
        def test_func(data: Dict[str, Any]) -> Any:
            return data["__root__"]

        input_data = {}
        expected = {}
        assert test_func(input_data) == expected

    # -----------------------------
    # Combined Tests for `traverse_datastructures` and `root_node`
    # -----------------------------

    def test_combined_decorators_deep_nested(self):
        """Test `root_node` and `traverse_datastructures` on a deeply nested structure."""
        @root_node(param_index=0)
        @traverse_datastructures(ignore=["SKIP_ME"])
        def test_func(value: Any) -> Any:
            return lowercase(value)

        input_data = {
            "root_key": ["ITEM1", {"key1": "ITEM2", "SKIP_ME": "IGNORED"}],
            "key2": {"key3": ("ITEM3", {"deep_key": "ITEM4"})}
        }
        expected = {
            "root_key": ["item1", {"key1": "item2", "SKIP_ME": "ignored"}],
            "key2": {"key3": ("item3", {"deep_key": "item4"})}
        }
        assert test_func(input_data) == expected

    def test_combined_decorators_with_primitive_root(self):
        """Test `root_node` and `traverse_datastructures` when root is a primitive."""
        @root_node(param_index=0)
        @traverse_datastructures()
        def test_func(value: Any) -> Any:
            return lowercase(value)

        input_data = "ITEM1"
        expected = "item1"
        assert test_func(input_data) == expected

