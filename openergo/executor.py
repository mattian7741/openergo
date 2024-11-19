import re
from abc import ABC
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, cast

# Type variable for generic decorators
F = TypeVar("F", bound=Callable[..., Any])

# Function: deep_get


def deep_get(dic: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Recursively fetch a value from a nested dictionary using dot-separated keys.
    """
    keys: List[str] = key.split(".")
    for k in keys:
        dic = dic.get(k, default)
        if dic is default:
            break
    return dic


# Function: traverse_datastructures


def traverse_datastructures(
    ignore: Optional[List[str]] = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Traverses data structures (dict, list, tuple) to apply a function to their elements,
    with an option to ignore specific strings in keys or values.

    Args:
        ignore: List of exact strings to ignore during traversal. Default is None.
    """
    ignore_set: set[str] = set(ignore or [])

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(value: Any, *args: Tuple[Any, ...]) -> Any:
            handlers: Dict[type, Callable[[Any], Any]] = {
                dict: lambda _dict, *args: {
                    (k if is_hashable(k) and k in ignore_set else wrapper(k, *args)): (
                        v if is_hashable(v) and v in ignore_set else wrapper(v, *args)
                    )
                    for k, v in _dict.items()
                },
                list: lambda _list, *args: [
                    item if is_hashable(item) and item in ignore_set else wrapper(item, *args) for item in _list
                ],
                tuple: lambda _tuple, *args: tuple(
                    item if is_hashable(item) and item in ignore_set else wrapper(item, *args) for item in _tuple
                ),
            }

            # Test hashability using try/except to avoid edge-case failures
            if not is_hashable(value):
                return handlers.get(type(value), func)(value, *args)

            # If the value is hashable and in the ignore set, return it
            if value in ignore_set:
                return value

            # Default case: Use the appropriate handler or apply the function
            return handlers.get(type(value), func)(value, *args)

        def is_hashable(item: Any) -> bool:
            """Check if an item is hashable."""
            try:
                hash(item)
                return True
            except TypeError:
                return False

        return wrapper

    return decorator


# Function: root_node


def root_node(param_index: int = 0) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Convert args to a list to modify
            args_list: List[Any] = list(args)
            if param_index < len(args_list):
                args_list[param_index] = {"__root__": args_list[param_index]}
            elif param_index == 0 and "__root__" not in kwargs:
                kwargs["__root__"] = {"__root__": kwargs.get("__root__")}
            # Rebuild args as a tuple
            args = tuple(args_list)
            result: Any = func(*args, **kwargs)
            # Unwrap the root node before returning the result
            if isinstance(result, dict) and "__root__" in result:
                return result["__root__"]
            return result

        return cast(F, wrapper)  # Explicitly cast wrapper to type F

    return decorator


# Function: substitute


@root_node(param_index=1)  # Wrap the second parameter (data) in a root node
@traverse_datastructures()  # Traverse the data structure to apply substitutions
def substitute(value: Any, data: Dict[str, Any]) -> Any:
    """
    Perform substitutions on a value based on a configuration dictionary,
    resolving placeholders enclosed in `{}`.
    """
    if isinstance(value, str):
        prev_value: Optional[str] = None
        while prev_value != value:  # Recursively resolve substitutions
            prev_value = value
            value = re.sub(
                r"{([^}]*)}",  # Match content within curly braces
                lambda match: str(
                    deep_get(
                        data,
                        # Handle "{}" as "{__root__}" and prepend "__root__."
                        # to other keys
                        (
                            "__root__"
                            if not match.group(1)
                            else (
                                f"__root__.{match.group(1)}"
                                if not match.group(1).startswith("__root__.")
                                else match.group(1)
                            )
                        ),
                        # Default to the original placeholder if unresolved
                        match.group(0),
                    )
                ),
                value,
            )
    return value


# Function: substitutions


def substitutions(method: F) -> F:
    """
    Decorator to perform substitutions in `self.config` based on values enclosed in `{}`.
    """

    @wraps(method)
    def wrapper(self: "Executor", *args: Any, **kwargs: Any) -> Any:
        # Apply substitutions on the root node (entire config)
        self.config = substitute(self.config, self.config)
        return method(self, *args, **kwargs)

    return wrapper  # type: ignore


# Function: bindings


def bindings(method: F) -> F:
    """
    Decorator to inject arguments into the `execute` method based on `self.config['input']['bindings']`.
    """

    @wraps(method)
    def wrapper(self: "Executor", *args: Any, **kwargs: Any) -> Any:
        config_bindings: Dict[str, Any] = self.config.get("input", {}).get("bindings", {})
        if not isinstance(config_bindings, dict):
            raise ValueError("config['input']['bindings'] must be a dictionary.")

        # Inject bindings into kwargs
        kwargs.update(config_bindings)
        return method(self, *args, **kwargs)

    return wrapper  # type: ignore


# Class: Executor


class Executor(ABC):
    """
    Abstract base class for executors, implementing the `execute` method with substitutions and bindings.
    """

    def __init__(self, function: Callable[..., Any], config: Optional[Dict[str, Any]] = None) -> None:
        self.function: Callable[..., Any] = function
        self.config: Dict[str, Any] = config or {}

    @substitutions
    @bindings
    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute the executor. Substitutions and bindings are applied before execution.
        """
        return self.function(*args, **kwargs)
