import dill
import base64

def serialize_text(text: str) -> str:
    if not isinstance(text, str):  # Type check to ensure input is a string
        raise TypeError("Input must be a string")
    serialized = dill.dumps(text)  # Serialize text using dill
    encoded = base64.b64encode(serialized).decode('utf-8')  # Encode to a string
    return encoded

def test_serialize():
    failed_tests = []  # List to collect failed test messages

    def assert_equal(a, b, message=""):
        if a != b:
            failed_tests.append(f"Test failed: {message} | Expected {b}, got {a}")
            return False
        return True

    # Test cases
    # Test serialization of a regular string
    text = "Hello, world!"
    serialized = serialize_text(text)
    deserialized = dill.loads(base64.b64decode(serialized))
    assert_equal(deserialized, text, "Regular text serialization")

    # Test serialization of a string with special characters
    text = "!@#$%^&*()_+-=~`{}|[]\\:\";'<>?,./"
    serialized = serialize_text(text)
    deserialized = dill.loads(base64.b64decode(serialized))
    assert_equal(deserialized, text, "Special characters serialization")

    # Test serialization of a string with Unicode characters
    text = "你好，世界！😊"
    serialized = serialize_text(text)
    deserialized = dill.loads(base64.b64decode(serialized))
    assert_equal(deserialized, text, "Unicode characters serialization")

    # Test serialization of an empty string
    text = ""
    serialized = serialize_text(text)
    deserialized = dill.loads(base64.b64decode(serialized))
    assert_equal(deserialized, text, "Empty string serialization")

    # Test serialization of a very long string
    text = "a" * 10000  # String of length 10,000
    serialized = serialize_text(text)
    deserialized = dill.loads(base64.b64decode(serialized))
    assert_equal(deserialized, text, "Long string serialization")

    # Test serialization of a string with whitespace only
    text = "    \t\n"
    serialized = serialize_text(text)
    deserialized = dill.loads(base64.b64decode(serialized))
    assert_equal(deserialized, text, "Whitespace-only string serialization")

    # Ensure the function raises an error for non-string input
    try:
        serialize_text(1234)  # Attempt to serialize an integer
    except TypeError:
        pass  # Test passes if TypeError is raised
    else:
        failed_tests.append("Non-string input test failed (TypeError not raised).")

    # Print summary
    if not failed_tests:
        print("All tests passed!")
    else:
        print("Some tests failed:")
        for failure in failed_tests:
            print(failure)

if __name__ == "__main__":
    test_serialize()
