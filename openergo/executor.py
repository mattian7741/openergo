import re
from abc import ABC
from functools import wraps
from typing import Any, Callable, Dict, Match, Tuple, TypeVar, Union

F = TypeVar("F", bound=Callable[..., Any])


def deep_get(dic: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Recursively fetch a value from a nested dictionary using dot-separated keys.
    """
    keys = key.split(".")
    for k in keys:
        dic = dic.get(k, default)
        if dic is default:
            break
    return dic


def traverse_datastructures(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Traverses data structures (dict, list, tuple) to apply a function to their elements.
    """
    @wraps(func)
    def wrapper(value: Any, *args: Tuple[Any, ...]) -> Any:
        handlers: Dict[type, Callable[[Any], Any]] = {
            dict: lambda _dict, *args: {wrapper(key, *args): wrapper(val, *args) for key, val in _dict.items()},
            list: lambda _list, *args: [wrapper(item, *args) for item in _list],
            tuple: lambda _tuple, *args: tuple(wrapper(item, *args) for item in _tuple),
        }
        return handlers.get(type(value), func)(value, *args)

    return wrapper


def root_node(param_index: int = 0) -> Callable[[F], F]:
    """
    Decorator to wrap a specific parameter of the target function into an anonymous root node.
    
    Args:
        param_index: Index of the parameter to wrap with the root node. Default is 0 (first parameter).
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Convert the selected argument to a root node
            args = list(args)
            if param_index < len(args):
                args[param_index] = {"__root__": args[param_index]}
            elif param_index == 0 and "__root__" not in kwargs:
                kwargs["__root__"] = {"__root__": kwargs.get("__root__")}
            result = func(*args, **kwargs)
            # Unwrap the root node before returning the result
            if isinstance(result, dict) and "__root__" in result:
                return result["__root__"]
            return result
        return wrapper
    return decorator



@root_node(param_index=1)  # Wrap the second parameter (data) in a root node
@traverse_datastructures  # Traverse the data structure to apply substitutions
def substitute(value: Any, data: Dict[str, Any]) -> Any:
    """
    Perform substitutions on a value based on a configuration dictionary,
    resolving placeholders enclosed in `{}`.
    """
    if isinstance(value, str):
        prev_value = None
        while prev_value != value:  # Recursively resolve substitutions
            prev_value = value
            value = re.sub(
                r"{([^}]*)}",  # Match content within curly braces
                lambda match: str(
                    deep_get(
                        data,
                        # Handle "{}" as "{__root__}" and prepend "__root__." to other keys
                        "__root__" if not match.group(1) else f"__root__.{match.group(1)}"
                            if not match.group(1).startswith("__root__.") else match.group(1),
                        match.group(0)  # Default to the original placeholder if unresolved
                    )
                ),
                value,
            )
    return value




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


def bindings(method: F) -> F:
    """
    Decorator to inject arguments into the `execute` method based on `self.config['input']['bindings']`.
    """
    @wraps(method)
    def wrapper(self: "Executor", *args: Any, **kwargs: Any) -> Any:
        bindings: Dict[str, Any] = self.config.get("input", {}).get("bindings", {})
        if not isinstance(bindings, dict):
            raise ValueError("config['input']['bindings'] must be a dictionary.")

        # Inject bindings into kwargs
        kwargs.update(bindings)
        return method(self, *args, **kwargs)

    return wrapper  # type: ignore


class Executor(ABC):
    """
    Abstract base class for executors, implementing the `execute` method with substitutions and bindings.
    """

    def __init__(self, function: Callable[..., Any], config: Union[Dict[str, Any], None] = None) -> None:
        self.function: Callable[..., Any] = function
        self.config: Dict[str, Any] = config or {}

    @substitutions
    @bindings
    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute the executor. Substitutions and bindings are applied before execution.
        """
        return self.function(*args, **kwargs)
