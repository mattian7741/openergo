import re
from abc import ABC
from functools import wraps
from typing import Any, Generator, Union, Callable, Dict, List, Optional, Tuple, TypeVar, cast
import json
from openergo.utility import Utility, traverse_datastructures
F = TypeVar("F", bound=Callable[..., Any])
from openergo.colors import *



# def traverse_datastructures(
#     ignore: Optional[List[str]] = None,
# ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
#     ignore_set: set[str] = set(ignore or [])

#     def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
#         @wraps(func)
#         def wrapper(value: Any, *args: Tuple[Any, ...]) -> Any:
#             handlers: Dict[type, Callable[[Any], Any]] = {
#                 dict: lambda _dict, *args: {
#                     (k if is_hashable(k) and k in ignore_set else wrapper(k, *args)): (
#                         v if is_hashable(
#                             v) and v in ignore_set else wrapper(v, *args)
#                     )
#                     for k, v in _dict.items()
#                 },
#                 list: lambda _list, *args: [
#                     item if is_hashable(item) and item in ignore_set else wrapper(item, *args) for item in _list
#                 ],
#                 tuple: lambda _tuple, *args: tuple(
#                     item if is_hashable(item) and item in ignore_set else wrapper(item, *args) for item in _tuple
#                 ),
#             }

#             if not is_hashable(value):
#                 return handlers.get(type(value), func)(value, *args)

#             if value in ignore_set:
#                 return value

#             return handlers.get(type(value), func)(value, *args)

#         def is_hashable(item: Any) -> bool:
#             try:
#                 hash(item)
#                 return True
#             except TypeError:
#                 return False

#         return wrapper

#     return decorator



# def root_node(param_index: int = 0) -> Callable[[F], F]:
#     def decorator(func: F) -> F:
#         @wraps(func)
#         def wrapper(*args: Any, **kwargs: Any) -> Any:
#             # Convert args to a list to modify
#             args_list: List[Any] = list(args)
#             if param_index < len(args_list):
#                 args_list[param_index] = {"__root__": args_list[param_index]}
#             elif param_index == 0 and "__root__" not in kwargs:
#                 kwargs["__root__"] = {"__root__": kwargs.get("__root__")}
#             # Rebuild args as a tuple
#             args = tuple(args_list)
#             result: Any = func(*args, **kwargs)
#             # Unwrap the root node before returning the result
#             if isinstance(result, dict) and "__root__" in result:
#                 return result["__root__"]
#             return result

#         return cast(F, wrapper)  # Explicitly cast wrapper to type F

#     return decorator

# def is_complete_substitution(value: str) -> bool:
#     if not value.startswith("{") or not value.endswith("}"):
#         return False

#     # Define a regex pattern for allowed characters and invalid sequences
#     pattern = r'^[\{\}\.\s\t\w]*$'  # Valid characters
#     invalid_dot_sequences = r'\{\.|\.}'  # Forbidden sequences {. and .}

#     # Check if the string contains only valid characters
#     if not re.fullmatch(pattern, value):
#         return False

#     # Check for invalid sequences
#     if re.search(invalid_dot_sequences, value):
#         return False

#     # Ensure all opening `{` have matching closing `}` using a stack
#     stack = []
#     for char in value:
#         if char == '{':
#             stack.append(char)
#         elif char == '}':
#             if not stack:  # Closing brace without an opening
#                 return False
#             stack.pop()

#     # If the stack is not empty, there's an unmatched opening brace
#     return not stack


# # @root_node
# @traverse_datastructures
# def substitute(value: Any, data: Union[str, int, float, bool, list, dict, tuple]) -> Any:
#     def resolve(value: str, previous=[]) -> str:
#         pattern = re.compile(r"\{([^{}]*)\}")

#         while value != previous:  # Keep resolving until no changes
#             previous = value
            
#             def substitution(match):
#                 match_group = match.group(1)
#                 print(f"\nEvaluating match group (type: {type(match_group).__name__}):\n{JSON}{json.dumps(match_group, indent=3)}{RESET}")

#                 resolved_key = resolve(match_group)
#                 print(f"\nResolved key (type: {type(resolved_key).__name__}):\n{JSON}{json.dumps(resolved_key, indent=3)}{RESET}")


#                 print(f"Match.group(0):\n{JSON}{json.dumps(match.group(0), indent=3)}{RESET}")
#                 print(f"Value:\n{JSON}{json.dumps(value, indent=3)}{RESET}")

#                 if match.group(0) == value:
#                     resolved_value = Utility.deep_get(data, resolved_key, match.group(0))
#                     print(f"\nResolved value for key {resolved_key} (type: {type(resolved_value).__name__}):\n{JSON}{json.dumps(resolved_value, indent=3)}{RESET}")
#                     return resolved_value
                

#                 resolved_partial = str(Utility.deep_get(data, resolved_key, match.group(0)))
#                 print(f"\nPartially resolved value (type: {type(resolved_partial).__name__}):\n{JSON}{json.dumps(resolved_partial, indent=3)}{RESET}")
                
#                 # if (match.group(0) == value):
#                 #     return resolved_partial
#                 return str(resolved_partial)

#             print(f"\nAttempting substitution for value (type: {type(value).__name__}):\n{JSON}{json.dumps(value, indent=3)}{RESET}")
#             value = pattern.sub(substitution, value)  # Use the defined substitution function
#             print(f"\nUpdated value after substitution (type: {type(value).__name__}):\n{JSON}{json.dumps(value, indent=3)}{RESET}")
        
#         return value

#     print(f"\nStarting resolution for value (type: {type(value).__name__}):\n{JSON}{json.dumps(value, indent=3)}{RESET}")


#     resolved = resolve(value) if isinstance(value, str) else value
#     print(f"\nFinal resolved value (type: {type(resolved).__name__}):\n{JSON}{json.dumps(resolved, indent=3)}{RESET}")
#     return resolved



def is_complete_substitution(value: str) -> bool:
    print(f"\nChecking if value is a complete substitution (type: {type(value).__name__}):\n{JSON}{json.dumps(value, indent=3)}{RESET}")

    if not value.startswith("{") or not value.endswith("}"):
        print(f"Value does not start and end with braces: {value}")
        return False

    pattern = r'^[\{\}\.\s\t\w]*$'  # Valid characters
    invalid_dot_sequences = r'\{\.|\.}'  # Forbidden sequences {. and .}

    if not re.fullmatch(pattern, value):
        print(f"Value contains invalid characters: {value}")
        return False

    if re.search(invalid_dot_sequences, value):
        print(f"Value contains invalid dot sequences: {value}")
        return False

    stack = []
    for char in value:
        if char == '{':
            stack.append(char)
        elif char == '}':
            if not stack:  # Closing brace without an opening
                print(f"Unmatched closing brace in value: {value}")
                return False
            stack.pop()

    result = not stack
    print(f"Complete substitution result for {value}: {result}")
    return result

@traverse_datastructures
def substitute(value: Any, data: Union[str, int, float, bool, list, dict, tuple]) -> Any:
    def resolve(value: str, depth: int = 0) -> Any:
        print(f"\nResolving value (depth={depth}, type: {type(value).__name__}):\n{JSON}{json.dumps(value, indent=3)}{RESET}")
        pattern = re.compile(r"\{([^{}]*)\}")
        previous = None

        while value != previous:  # Keep resolving until no changes
            previous = value
            print(f"Previous value at depth {depth}:\n{JSON}{json.dumps(previous, indent=3)}{RESET}")

            def substitution(match):
                match_group = match.group(1)
                print(f"Matched group (type: {type(match_group).__name__}):\n{JSON}{json.dumps(match_group, indent=3)}{RESET}")

                resolved_key = resolve(match_group, depth + 1)
                print(f"Resolved key for {match_group} (depth={depth+1}):\n{JSON}{json.dumps(resolved_key, indent=3)}{RESET}")

                resolved_value = Utility.deep_get(data, resolved_key, match.group(0))
                print(f"Resolved value for key {resolved_key} (depth={depth+1}):\n{JSON}{json.dumps(resolved_value, indent=3)}{RESET}")

                # Determine whether to cast to string
                if depth > 0 or value != match.group(0):
                    result = str(resolved_value)
                    print(f"Returning string-cast resolved value (depth={depth}):\n{JSON}{json.dumps(result, indent=3)}{RESET}")
                    return result

                print(f"Returning original resolved value (depth={depth}):\n{JSON}{json.dumps(resolved_value, indent=3)}{RESET}")
                return resolved_value

            # Attempt substitution and handle non-string results
            try:
                new_value = pattern.sub(substitution, value)
                print(f"Updated value after substitution (depth={depth}, type: {type(new_value).__name__}):\n{JSON}{json.dumps(new_value, indent=3)}{RESET}")
                value = new_value
            except TypeError as e:
                print(f"Non-string substitution result detected (type: {type(value).__name__}):\n{JSON}{json.dumps(value, indent=3)}{RESET}")
                break  # Non-string values terminate the substitution process

        # At the root level, decide type based on whether it's a complete substitution
        if depth == 0 and is_complete_substitution(value):
            resolved_key = resolve(value[1:-1], depth + 1)  # Remove outer braces
            print(f"Root level complete substitution for {value}:\n{JSON}{json.dumps(resolved_key, indent=3)}{RESET}")
            result = Utility.deep_get(data, resolved_key, value)
            print(f"Final resolved value at root (depth={depth}):\n{JSON}{json.dumps(result, indent=3)}{RESET}")
            return result

        print(f"Final resolved value at depth {depth}:\n{JSON}{json.dumps(value, indent=3)}{RESET}")
        return value

    if isinstance(value, str):
        print(f"\nStarting substitution for value (type: {type(value).__name__}):\n{JSON}{json.dumps(value, indent=3)}{RESET}")
        result = resolve(value)
        print(f"\nFinal substituted value (type: {type(result).__name__}):\n{JSON}{json.dumps(result, indent=3)}{RESET}")
        return result

    print(f"\nNon-string value passed, returning as is (type: {type(value).__name__}):\n{JSON}{json.dumps(value, indent=3)}{RESET}")
    return value




def contextualize(method: F) -> F:
    @wraps(method)
    def wrapper(self: "Executor", data) -> Any:
        print(f"Entering contextualize with input:\n{JSON}{json.dumps(data, indent=3)}{RESET}")
        
        context = {"config": self.config, "input": data}
        print(f"Created context:\n{JSON}{json.dumps(context, indent=3)}{RESET}")
        
        for result in method(self, context):
            print(f"Yielding from contextualize:\n{JSON}{json.dumps(result['output'], indent=3)}{RESET}")
            yield result["output"]
        
    return wrapper  # type: ignore


def substitutions(method: F) -> F:
    @wraps(method)
    def wrapper(self: "Executor", data) -> Any:
        print(f"Entering substitutions with input:\n{JSON}{json.dumps(data, indent=3)}{RESET}")

        context = substitute(data, data)
        print(f"Initial substitution context:\n{JSON}{json.dumps(context, indent=3)}{RESET}")

        for result in method(self, context):
            print(f"Method result before substitution:\n{JSON}{json.dumps(result, indent=3)}{RESET}")
            context = substitute(result, result)
            print(f"Updated substitution context:\n{JSON}{json.dumps(context, indent=3)}{RESET}")
            print("Yielding from substitutions")
            yield context
        
    return wrapper  # type: ignore


def bindings(method: F) -> F:
    @wraps(method)
    def wrapper(self: "Executor", data, *args: Any, **kwargs: Any) -> Any:
        print(f"Entering bindings with input:\n{JSON}{json.dumps(data, indent=3)}{RESET}")

        config_bindings: Dict[str, Any] = data.get(
            "config", {}).get("input", {}).get("bindings", {})

        print(f"Extracted config bindings:\n{JSON}{json.dumps(config_bindings, indent=3)}{RESET}")

        if not isinstance(config_bindings, dict):
            raise ValueError("config['input']['bindings'] must be a dictionary.")

        for result in method(self, **config_bindings):
            print(f"Method result:\n{JSON}{json.dumps(result, indent=3)}{RESET}")
            data["output"] = result
            print(f"Updated data:\n{JSON}{json.dumps(data, indent=3)}{RESET}")
            print("Yielding from bindings")
            yield data
        
    return wrapper  # type: ignore


def serialization(method: F) -> F:
    @wraps(method)
    def wrapper(self: "Executor", data) -> Any:
        print(f"Entering serialization with input:\n{JSON}{json.dumps(data, indent=3)}{RESET}")
        
        deserialized = Utility.deserialize(data)
        print(f"Deserialized data:\n{JSON}{json.dumps(deserialized, indent=3)}{RESET}")
        
        for result in method(self, deserialized):
            print(f"Method result before serialization:\n{JSON}{json.dumps(result, indent=3)}{RESET}")
            serialized = Utility.serialize(result)
            print(f"Serialized result:\n{JSON}{json.dumps(serialized, indent=3)}{RESET}")
            print("Yielding from serialization")
            yield serialized
        
    return wrapper  # Explicit typing enforced


def encryption(method: F) -> F:
    @wraps(method)
    def wrapper(self: "Executor", data) -> Any:
        print(f"Entering encryption with input:\n{JSON}{json.dumps(data, indent=3)}{RESET}")

        ENCRYPTIONKEY = 'AgUpjQf8Pbe609pLrGnem6PEoawnt3wu1dWzbvgZfPo='
        decrypted = Utility.decrypt(data, "input.payload.encrypted", ENCRYPTIONKEY)
        print(f"Decrypted data:\n{JSON}{json.dumps(decrypted, indent=3)}{RESET}")

        for result in method(self, decrypted):
            print(f"Method result:\n{JSON}{json.dumps(result, indent=3)}{RESET}")
            print("Yielding from encryption")
            yield result
            # Uncomment to enable re-encryption:
            # encrypted = Utility.encrypt(result, "output", ENCRYPTIONKEY)
            # print(f"Re-encrypted result:\n{JSON}{json.dumps(encrypted, indent=3)}{RESET}")
        
    return wrapper  # Explicit typing enforced


def exceptions(func: Callable[..., Generator[Any, None, None]]) -> Callable[..., Generator[Any, None, None]]:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Generator[Any, None, None]:
        print(f"Entering exceptions with args:\n{JSON}{json.dumps(args, indent=3)}{RESET}, kwargs:\n{JSON}{json.dumps(kwargs, indent=3)}{RESET}")
        try:
            yield from func(*args, **kwargs)
        except Exception as exc:  # pylint: disable=broad-except
            print(f"Exception caught:\n{JSON}{json.dumps({'error': str(exc)}, indent=3)}{RESET}")
        print("Exiting exceptions")
    return wrapper

class Executor(ABC):

    def __init__(self, function: Callable[..., Any],
                 config: Optional[Dict[str, Any]] = None) -> None:
        self.function: Callable[..., Any] = function
        # self.generator = Utility.generatorize(function)
        self.config: Dict[str, Any] = config or {}

    #@exceptions
    # @unbatching
    # @batching
    #@contextualize
    # @substitutions
    # @passbyreference
    #@encryption
    # @compression
    #@serialization
    # @chunking
    # @streaming
    # @validation
    # @transactions
    #@substitutions
    # @mapping
    #@bindings

    # @exceptions
    @contextualize
    @encryption
    @serialization
    @substitutions
    @bindings
    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute the executor. Substitutions and bindings are applied before execution.
        """
        for result in Utility.generatorize(self.function)(*args, **kwargs):
            yield result
