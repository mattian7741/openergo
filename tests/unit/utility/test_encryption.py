from openergo.utility import Utility  # Import the Utility class
from cryptography.fernet import Fernet


class TestEncryption:
    def setup_method(self):
        """Set up a unique encryption key and sample data for each test run."""
        self.key = Fernet.generate_key().decode("utf-8")  # Generate a new key at runtime
        self.fernet = Fernet(self.key)  # Create a Fernet instance with the generated key
        self.data = {'data': 'Sensitive information'}

    def test_encrypt_data(self):
        """Test encryption of data with the runtime-generated key."""
        encrypted = Utility.encrypt('Sensitive information', self.key)  # Call the static method from Utility
        assert 'Sensitive information' != encrypted

    def test_decrypt_data(self):
        """Test decryption back to original data with the runtime-generated key."""
        encrypted = Utility.encrypt('Sensitive information', self.key)  # Call the static method from Utility
        decrypted = Utility.decrypt(encrypted, self.key)  # Call the static method from Utility
        assert decrypted == 'Sensitive information'
