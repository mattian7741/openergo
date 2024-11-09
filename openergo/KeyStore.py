import os
import json
from abc import ABC, abstractmethod
from typing import Optional

class KeyStoreBase(ABC):
    """
    Abstract base class for a key store interface.
    Concrete implementations should provide methods for storing, retrieving,
    and deleting keys.
    """

    @abstractmethod
    def store_key(self, key: str, value: str) -> None:
        """
        Store a key-value pair in the key store.
        
        Args:
            key (str): The key to store.
            value (str): The value associated with the key.
        """
        pass

    @abstractmethod
    def retrieve_key(self, key: str) -> Optional[str]:
        """
        Retrieve the value associated with a key.
        
        Args:
            key (str): The key to retrieve.
        
        Returns:
            Optional[str]: The value associated with the key, or None if the key does not exist.
        """
        pass

    @abstractmethod
    def delete_key(self, key: str) -> None:
        """
        Delete a key-value pair from the key store.
        
        Args:
            key (str): The key to delete.
        """
        pass

    @abstractmethod
    def list_keys(self) -> list[str]:
        """
        List all keys currently in the key store.
        
        Returns:
            list[str]: A list of all keys.
        """
        pass

class LocalDiskKeyStore(KeyStoreBase):
    """
    A local disk-based implementation of the key store. Keys and values
    are stored in a JSON file on disk.
    """

    def __init__(self, storage_file: str):
        self.storage_file = storage_file
        # Initialize storage file if it does not exist
        if not os.path.exists(self.storage_file):
            with open(self.storage_file, 'w') as file:
                json.dump({}, file)

    def _load_data(self) -> dict:
        """Load key-value pairs from the storage file."""
        with open(self.storage_file, 'r') as file:
            return json.load(file)

    def _write_data(self, data: dict) -> None:
        """Write key-value pairs to the storage file."""
        with open(self.storage_file, 'w') as file:
            json.dump(data, file)

    def store_key(self, key: str, value: str) -> None:
        """Store a key-value pair in the JSON file."""
        data = self._load_data()
        data[key] = value
        self._write_data(data)

    def retrieve_key(self, key: str) -> Optional[str]:
        """Retrieve a value by its key from the JSON file."""
        data = self._load_data()
        return data.get(key)

    def delete_key(self, key: str) -> None:
        """Delete a key-value pair from the JSON file."""
        data = self._load_data()
        if key in data:
            del data[key]
            self._write_data(data)

    def list_keys(self) -> list[str]:
        """List all keys in the JSON file."""
        data = self._load_data()
        return list(data.keys())
