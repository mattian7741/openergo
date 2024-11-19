def camel_case(string):
    return ''.join(word.capitalize() for word in string.split())

def test_camel_case():
    assert camel_case("hello world") == "HelloWorld"
    assert camel_case(" multiple words here ") == "MultipleWordsHere"
    assert camel_case("alreadyCamelCase") == "Alreadycamelcase"
    assert camel_case("") == ""


if __name__ == "__main__":
    test_camel_case()