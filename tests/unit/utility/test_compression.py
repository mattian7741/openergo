from openergo.utility import Utility

class TestCompression:
    def test_compress_data(self):
        """Test compression of JSON serializable data."""
        data = {'data': 'This is a test string for compression.'}
        compressed = Utility.compress(data)
        assert isinstance(compressed, str)

    def test_uncompress_data(self):
        """Test decompression to original data."""
        data = {'data': 'This is a test string for compression.'}
        compressed = Utility.compress(data)
        uncompressed = Utility.uncompress(compressed)
        assert uncompressed == data
