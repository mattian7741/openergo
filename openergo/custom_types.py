from typing import Dict, List, TypedDict, Union

# T = TypeVar("T")

JsonList = List["JsonType"]
JsonDict = Dict[str, "JsonType"]
JsonType = Union[int, float, str, bool, None, JsonList, JsonDict]


class TypedDictType(TypedDict):
    pass
