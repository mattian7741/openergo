from openergo.utility import Utility  # Import the Utility class directly


class TestDataManipulation:
    def setup_method(self):
        """Set up test case variables."""
        self.data = {
            'a': {'b': {'c': 10}},
            'x': {'y': {'z': 20}},
            'p': {'q': {'r': 30}}
        }

    def test_deep_get_existing_key(self):
        """Test deep_get retrieves the correct value for existing key."""
        result = Utility.deep_get(self.data, 'a.b.c')
        assert result == 10

    def test_deep_get_non_existing_key(self):
        """Test deep_get raises KeyError for non-existing key."""
        try:
            Utility.deep_get(self.data, 'x.y.not_exists')
        except KeyError:
            assert True
        else:
            assert False, "Expected KeyError was not raised."

    def test_deep_get_with_default(self):
        """Test deep_get returns a default value when the key is missing."""
        result = Utility.deep_get(self.data, 'p.q.r.missing', default_sentinel=42)
        assert result == 42

    def test_deep_set_existing_key(self):
        """Test deep_set correctly modifies an existing key."""
        Utility.deep_set(self.data, 'p.q.r', 100)
        assert self.data['p']['q']['r'] == 100

    def test_deep_set_new_key(self):
        """Test deep_set creates and sets a new key."""
        Utility.deep_set(self.data, 'a.b.d', 40)
        assert self.data['a']['b']['d'] == 40

    def test_deep_unset_existing_key(self):
        """Test deep_unset correctly removes an existing key."""
        Utility.deep_unset(self.data, 'x.y.z')
        assert 'z' not in self.data['x']['y']

    def test_deep_unset_non_existing_key(self):
        """Test deep_unset handles non-existing key without error."""
        Utility.deep_unset(self.data, 'p.q.non_exist')
        assert 'non_exist' not in self.data['p']['q']  # Key shouldn't exist, and no error should occur
