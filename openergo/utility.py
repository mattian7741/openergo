import base64
import hashlib
import json
import lzma
import types
import uuid as uuid_lib
from datetime import datetime, timezone
from functools import wraps
from io import StringIO
from typing import (Any, Callable, Dict, Generator, Iterator, List, Optional,
                    Tuple, Type, Union, cast, get_origin)

import dill
import pydash
from cryptography.fernet import Fernet

_NO_VALUE: object = object()


class Utility:
    @staticmethod
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

    @staticmethod
    def root_node(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(value: Any, key: str, *args: Any) -> Any:
            if key == "":
                return value
            result: Any = func({"__root__": value}, f"__root__.{key}", *args)
            return result.get("__root__", result) if isinstance(result, dict) else result

        return wrapper

    @staticmethod
    def deep_get(data: Any, key: str, default_sentinel: Any = _NO_VALUE) -> Any:
        if not pydash.has(data, key) and default_sentinel is _NO_VALUE:
            raise KeyError(f"Key '{key}' not found in the provided data.")
        return pydash.get(data, key, default_sentinel)

    @staticmethod
    def deep_set(data: Any, key: str, val: Any) -> Any:
        pydash.set_(data, key, val)
        return data

    @staticmethod
    def deep_unset(data: Any, key: str) -> Any:
        nested: Any = data
        keys: List[str] = key.split(".")
        try:
            for k in keys[:-1]:
                nested = nested[int(k) if isinstance(nested, list) else k]
            del nested[int(keys[-1]) if isinstance(nested, list) else keys[-1]]
        except (KeyError, IndexError, ValueError):
            pass
        return data

    @staticmethod
    def unique_identifier(prefix: str = "") -> str:
        return f"{prefix}{['', '_'][bool(prefix)]}{Utility.utc_string()}{Utility.uuid()[:8]}"

    @staticmethod
    def utc_string(prefix: str = "") -> str:
        return f"{prefix}{['', '_'][bool(prefix)]}{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"

    @staticmethod
    def uuid(prefix: str = "") -> str:
        return f"{prefix}{['', '_'][bool(prefix)]}{str(uuid_lib.uuid4())}"

    @staticmethod
    def hash(string: str, prefix: str = "") -> str:
        return f"{prefix}{['', '_'][bool(prefix)]}{hashlib.md5(string.encode('utf-8')).hexdigest()}"

    @staticmethod
    def stringify(obj: Any) -> str:
        return (
            "null"
            if obj is None
            else json.dumps(obj) if isinstance(obj, (dict, list, str, int, float, bool)) else str(obj)
        )

    @staticmethod
    def objectify(stringified: str) -> Union[List[Any], Dict[str, Any], None]:
        return cast(Union[List[Any], Dict[str, Any], None], json.loads(stringified))

    @staticmethod
    def serialize(obj: Any) -> Any:
        return (
            obj
            if isinstance(obj, (type(None), bool, int, float, str))
            else (obj.serialize() if hasattr(obj, "serialize") else base64.b64encode(dill.dumps(obj)).decode("utf-8"))
        )

    @staticmethod
    def deserialize(serialized: str) -> Any:
        return (
            serialized
            if not serialized
            else (
                dill.loads(base64.b64decode(serialized.encode("utf-8"))) if isinstance(serialized, str) else serialized
            )
        )

    @staticmethod
    def compress(data: Any) -> str:
        return base64.b64encode(lzma.compress(json.dumps(data).encode("utf-8"))).decode("utf-8")

    @staticmethod
    def uncompress(data: str) -> Any:
        return json.loads(lzma.decompress(base64.b64decode(data)).decode("utf-8"))

    @staticmethod
    def encrypt(data: Any, encryptkey: str) -> str:
        return Fernet(encryptkey.encode("utf-8")).encrypt(str(data).encode("utf-8")).decode("utf-8")

    @staticmethod
    def decrypt(encrypted_data: str, encryptkey: str) -> str:
        return Fernet(encryptkey.encode("utf-8")).decrypt(encrypted_data.encode("utf-8")).decode("utf-8")

    @staticmethod
    def is_array(obj: Any) -> bool:
        return isinstance(obj, (list, set, tuple, types.GeneratorType))

    @staticmethod
    def safecast(expected_type: Type[Any], provided_value: Any) -> Any:
        value_type: Optional[Type[Any]] = get_origin(expected_type) or expected_type
        primitive_types: List[Type[Any]] = [
            int,
            float,
            complex,
            bool,
            str,
            bytes,
            bytearray,
            memoryview,
            list,
            tuple,
            range,
            set,
            frozenset,
            dict,
        ]

        if value_type in primitive_types:
            if value_type == tuple:
                return Utility._cast_to_tuple(provided_value)

            if value_type == bytes:
                return Utility._cast_to_bytes(provided_value)

            if value_type == bool:
                return Utility._cast_to_bool(provided_value)

            return Utility._cast_to_primitive(value_type, provided_value)

        if not callable(value_type) or value_type not in primitive_types:
            raise TypeError(
                f"Cannot cast {
                    provided_value!r} to unsupported type {expected_type}"
            )

        # Safely return without using cast, since it's not valid here.
        return provided_value

    @staticmethod
    def _cast_to_tuple(provided_value: Any) -> Any:
        if not isinstance(provided_value, (tuple, list, set, frozenset, range, dict)):
            raise TypeError(f"Cannot cast non-iterable {provided_value!r} to tuple")
        return tuple(provided_value)

    @staticmethod
    def _cast_to_bytes(provided_value: Any) -> bytes:
        if isinstance(provided_value, str):
            return provided_value.encode("utf-8")
        if isinstance(provided_value, (bytearray, memoryview)):
            return bytes(provided_value)
        raise TypeError(f"Cannot cast {provided_value!r} to bytes")

    @staticmethod
    def _cast_to_bool(provided_value: Any) -> bool:
        if isinstance(provided_value, str):
            return Utility._cast_str_to_bool(provided_value)
        if isinstance(provided_value, int):
            if provided_value in [0, 1]:
                return bool(provided_value)
            raise TypeError(f"Cannot cast non-boolean-like value {provided_value!r} to bool")
        raise TypeError(f"Cannot cast non-boolean-like value {provided_value!r} to bool")

    @staticmethod
    def _cast_str_to_bool(provided_str: str) -> bool:
        provided_str = provided_str.lower()
        if provided_str == "true":
            return True
        if provided_str in ("false", ""):
            return False
        raise TypeError(f"Cannot cast non-boolean-like value {provided_str!r} to bool")

    @staticmethod
    def _cast_to_primitive(value_type: Type[Any], provided_value: Any) -> Any:
        try:
            return value_type(provided_value)
        except (TypeError, ValueError) as e:
            raise TypeError(
                f"Cannot cast {
                    provided_value!r} to {value_type}"
            ) from e

    @staticmethod
    def json_text_to_object(plaintext: str) -> Iterator[Any]:
        return Utility.json_stream_to_object(StringIO(plaintext))

    @staticmethod
    def json_stream_to_object(input_stream: StringIO) -> Generator[Any, None, None]:
        buffer: str = ""
        depth: int = 0
        in_string: bool = False
        escape: bool = False
        while char := input_stream.read(1):
            if char == '"' and not escape:
                in_string = not in_string
            if not in_string and char in "{[":
                if depth == 0 and buffer.strip():
                    yield json.loads(buffer)
                    buffer = ""
                depth += 1
            elif not in_string and char in "]}":
                depth -= 1
            buffer += char
            escape = char == "\\" and in_string and not escape
            if depth == 0 and buffer.strip() and not in_string:
                yield json.loads(buffer)
                buffer = ""
        if buffer.strip():
            yield json.loads(buffer)
