import importlib
from types import FunctionType
from typing import Any, Callable, Dict, Union

from openergo.executor import Executor


class PythonExecutor(Executor):
    """
    A concrete implementation of `Executor` that supports Python callables
    and fully qualified string paths for functions.
    """

    def __init__(
            self, function: Union[Callable[..., Any], str], config: Dict[str, Any]) -> None:
        # Resolve the function if it's a string, otherwise use it directly
        if isinstance(function, str):
            module_path, func_name = function.rsplit(".", 1)
            module = importlib.import_module(module_path)
            resolved_function: Callable[..., Any] = getattr(module, func_name)
        elif isinstance(function, FunctionType):
            resolved_function = function
        else:
            raise TypeError(
                "function must be a callable or a fully qualified string path")

        # Initialize parent class with resolved function and the required
        # config
        super().__init__(resolved_function, config)
