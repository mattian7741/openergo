def reverse(string):
    return string[::-1]

def test_reverse():
    assert reverse("hello") == "olleh"
    assert reverse(" ") == " "
    assert reverse("12345") == "54321"
    assert reverse("!@#") == "#@!"

if __name__ == "__main__":
	test_reverse()