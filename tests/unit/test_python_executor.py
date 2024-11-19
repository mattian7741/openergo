import pytest
from unittest.mock import MagicMock, patch
from types import FunctionType
from openergo.python_executor import PythonExecutor


# Helper Functions for Testing
def sample_function(x, y):
    return x + y


# Test Cases
class TestPythonExecutor:
    def test_init_with_callable(self):
        """Test initialization with a function pointer."""
        config = {"key": "value"}  # Provide config as it's now required
        executor = PythonExecutor(function=sample_function, config=config)
        assert executor.function == sample_function
        assert isinstance(executor.function, FunctionType)
        assert executor.config == config  # Ensure config is passed correctly

    def test_init_with_string_reference(self):
        """Test initialization with a string reference to a function."""
        config = {"key": "value"}  # Provide config as it's now required
        with patch("importlib.import_module") as mock_import_module:
            mock_module = MagicMock()
            mock_function = MagicMock(return_value="mock_result")
            mock_module.mock_function = mock_function
            mock_import_module.return_value = mock_module

            executor = PythonExecutor(function="mock.module.mock_function", config=config)
            assert executor.function == mock_function
            assert executor.config == config  # Ensure config is passed correctly
            mock_import_module.assert_called_once_with("mock.module")

    def test_init_with_string_reference_invalid_path(self):
        """Test initialization with an invalid string reference."""
        config = {"key": "value"}  # Provide config as it's now required
        with patch("importlib.import_module", side_effect=ImportError):
            with pytest.raises(ImportError):
                PythonExecutor(function="invalid.module.function", config=config)

    def test_init_with_invalid_function_type(self):
        """Test initialization with an invalid function type."""
        config = {"key": "value"}  # Provide config as it's now required
        with pytest.raises(TypeError, match="function must be a callable or a fully qualified string path"):
            PythonExecutor(function=123, config=config)

    def test_execute_with_callable(self):
        """Test execution with a callable function."""
        config = {"key": "value"}  # Provide config as it's now required
        executor = PythonExecutor(function=sample_function, config=config)
        result = executor.execute(2, 3)
        assert result == 5

    def test_execute_with_string_reference(self):
        """Test execution with a string-referenced function."""
        config = {"key": "value"}  # Provide config as it's now required
        with patch("importlib.import_module") as mock_import_module:
            mock_module = MagicMock()
            mock_function = MagicMock(return_value=42)
            mock_module.mock_function = mock_function
            mock_import_module.return_value = mock_module

            executor = PythonExecutor(function="mock.module.mock_function", config=config)
            result = executor.execute(1, 2, foo="bar")
            assert result == 42
            mock_function.assert_called_once_with(1, 2, foo="bar")

    def test_config_is_set(self):
        """Test that the config is correctly set during initialization."""
        config = {"key": "value"}
        executor = PythonExecutor(function=sample_function, config=config)
        assert executor.config == config

    def test_execute_with_no_args(self):
        """Test execution with no arguments."""
        config = {"key": "value"}  # Provide config as it's now required
        no_arg_function = lambda: "no args"
        executor = PythonExecutor(function=no_arg_function, config=config)
        result = executor.execute()
        assert result == "no args"
