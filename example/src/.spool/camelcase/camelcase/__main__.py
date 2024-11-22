import json
from openergo.colors import *

def camel_case(string: str, dictionary: dict, integer: int) -> str:
    # Validate input types with corrected assertions
    assert isinstance(dictionary, dict), f"Expected 'dictionary' to be of type dict, got {type(dictionary).__name__}"
    assert isinstance(integer, int), f"Expected 'integer' to be of type int, got {type(integer).__name__}"
    assert isinstance(string, str), f"Expected 'string' to be of type str, got {type(string).__name__}"
    
    print(f"\nValidating inputs:")
    print(f"String:\n{JSON}{json.dumps(string, indent=3)}{RESET}")
    print(f"Dictionary:\n{JSON}{json.dumps(dictionary, indent=3)}{RESET}")
    print(f"Integer:\n{JSON}{json.dumps(integer, indent=3)}{RESET}")
    
    # Perform the camel case transformation
    result = ''.join(word.capitalize() for word in string.split())
    print(f"\nTransformed camel case result:\n{JSON}{json.dumps(result, indent=3)}{RESET}")
    
    return result


def test_camel_case():
    assert camel_case("hello world") == "HelloWorld"
    assert camel_case(" multiple words here ") == "MultipleWordsHere"
    assert camel_case("alreadyCamelCase") == "Alreadycamelcase"
    assert camel_case("") == ""


if __name__ == "__main__":
    test_camel_case()