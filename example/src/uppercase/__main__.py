def make_upper(string):
    return string.upper()

def test_make_upper():
    assert make_upper("hello") == "HELLO"
    assert make_upper("Hello World") == "HELLO WORLD"
    assert make_upper("") == ""
    assert make_upper("123!@#") == "123!@#"

if __name__ == "__main__":
    test_make_upper()