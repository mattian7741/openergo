def concatenate(string_list, delimiter="\n"):
    return delimiter.join(string_list)

def test_concatenate():
    assert concatenate(["hello", "world"]) == "hello\nworld"
    assert concatenate(["single"]) == "single"
    assert concatenate([]) == ""
    assert concatenate(["", ""]) == "\n"
    assert concatenate(["", "empty", ""]) == "\nempty\n"
    assert concatenate(["first", "", "last"]) == "first\n\nlast"
    assert concatenate(["line1", "line2\nline3", "line4"]) == "line1\nline2\nline3\nline4"
    assert concatenate([str(i) for i in range(3)]) == "0\n1\n2"
    

if __name__ == "__main__":
	test_concatenate()