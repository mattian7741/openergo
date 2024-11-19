import re

def snake_case(string):
    return re.sub(r'\s+', '_', string.strip())

def test_snake_case():
    assert snake_case(" hello world ") == "hello_world"
    assert snake_case("multiple   spaces") == "multiple_spaces"
    assert snake_case("already_snake_case") == "already_snake_case"
    assert snake_case(" leading and trailing ") == "leading_and_trailing"

if __name__ == "__main__":
    test_snake_case()