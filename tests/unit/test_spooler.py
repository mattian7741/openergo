import os
import pytest
import shutil
from unittest.mock import MagicMock, patch, mock_open, call
from openergo.spooler import Spooler


# Test Class
class TestSpooler:
    @pytest.fixture
    def spooler(self, tmp_path):
        """Fixture to provide a Spooler instance with a temporary folder."""
        folder_path = tmp_path / "test_project"
        os.makedirs(folder_path)
        return Spooler(folder_path)

    def test_init(self, spooler):
        """Test initialization of the Spooler instance."""
        assert os.path.basename(spooler.folder_path) == "test_project"
        assert spooler.project_name == "test_project"
        assert spooler.spool_dir.endswith(".spool")

    def test_setup_project_structure(self, spooler):
        """Test that the project structure is correctly set up."""
        with patch("shutil.copytree") as mock_copytree, \
             patch("os.makedirs") as mock_makedirs, \
             patch("builtins.open", mock_open()) as mock_file, \
             patch("shutil.ignore_patterns") as mock_ignore_patterns:

            # Simulate the ignore_patterns function returned by shutil
            mock_ignore = MagicMock()
            mock_ignore_patterns.return_value = mock_ignore

            spooler.setup_project_structure()

            # Assert directories were created
            mock_makedirs.assert_any_call(spooler.spool_dir, exist_ok=True)
            mock_makedirs.assert_any_call(spooler.project_spool_path, exist_ok=True)

            # Capture the actual ignore_patterns function used
            mock_copytree.assert_called_once_with(
                spooler.folder_path,
                spooler.package_dir,
                ignore=mock_ignore,  # Ensure the mocked ignore_patterns function is used
                dirs_exist_ok=True,
            )

            # Assert __init__.py was created
            init_file = os.path.join(spooler.package_dir, "__init__.py")
            mock_file.assert_called_once_with(init_file, "w", encoding="utf-8")

    def test_load_requirements_with_existing_file(self, spooler, tmp_path):
        """Test loading requirements when a requirements.txt file exists."""
        requirements_path = os.path.join(spooler.folder_path, "requirements.txt")
        requirements = ["package1", "package2"]
        with open(requirements_path, "w") as f:
            f.write("\n".join(requirements))

        spooler.load_requirements()
        assert spooler.requirements_txt == requirements

    def test_load_requirements_with_no_file(self, spooler):
        """Test loading requirements when no requirements.txt file exists."""
        spooler.load_requirements()
        assert spooler.requirements_txt == []

    def test_create_setup_file_with_existing_setup(self, spooler, tmp_path):
        """Test that an existing setup.py is copied to the project spool path."""
        existing_setup_path = os.path.join(spooler.folder_path, "setup.py")
        with open(existing_setup_path, "w") as f:
            f.write("# existing setup.py content")

        with patch("shutil.copy") as mock_copy:
            spooler.create_setup_file()
            mock_copy.assert_called_once_with(existing_setup_path, os.path.join(spooler.project_spool_path, "setup.py"))

    def test_create_setup_file_generate_new(self, spooler, tmp_path):
        """Test that a new setup.py file is generated if none exists."""
        setup_file_path = os.path.join(spooler.project_spool_path, "setup.py")
        os.makedirs(spooler.project_spool_path)

        with patch("builtins.open", mock_open()) as mock_file:
            spooler.create_setup_file()
            mock_file.assert_called_once_with(setup_file_path, "w", encoding="utf-8")
            written_content = mock_file().write.call_args[0][0]
            assert "setuptools" in written_content
            assert f"name=\"{spooler.project_name}\"" in written_content

    def test_spool_full_process(self, spooler):
        """Test the full spooling process."""
        with patch.object(spooler, "setup_project_structure") as mock_setup_structure, \
             patch.object(spooler, "load_requirements") as mock_load_requirements, \
             patch.object(spooler, "create_setup_file") as mock_create_setup:
            spooler.spool()
            mock_setup_structure.assert_called_once()
            mock_load_requirements.assert_called_once()
            mock_create_setup.assert_called_once()

    def test_main_function(self, tmp_path):
        """Test the main function integration."""
        folder_path = str(tmp_path / "test_project")
        os.makedirs(folder_path)

        with patch("sys.argv", ["script.py", folder_path]), \
             patch.object(Spooler, "spool") as mock_spool:
            from openergo import spooler
            spooler.main()
            mock_spool.assert_called_once()
