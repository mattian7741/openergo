import argparse
import os
import shutil
from typing import List


class Spooler:
    folder_path: str
    project_name: str
    spool_dir: str
    project_spool_path: str
    package_dir: str
    requirements_txt: List[str]

    def __init__(self, folder_path: str) -> None:
        self.folder_path = os.path.abspath(folder_path)
        self.project_name = os.path.basename(self.folder_path)
        self.spool_dir = os.path.join(
            os.path.dirname(
                self.folder_path), ".spool")
        self.project_spool_path = os.path.join(
            self.spool_dir, self.project_name)
        self.package_dir = os.path.join(
            self.project_spool_path, self.project_name)
        self.requirements_txt = []

    def setup_project_structure(self) -> None:
        os.makedirs(self.spool_dir, exist_ok=True)
        os.makedirs(self.project_spool_path, exist_ok=True)
        shutil.copytree(
            self.folder_path,
            self.package_dir,
            ignore=shutil.ignore_patterns(
                "*.toml", "*.md", "*.txt", "__pycache__"),
            dirs_exist_ok=True,
        )
        # Add this line to ensure the package has an __init__.py
        init_file: str = os.path.join(self.package_dir, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w", encoding="utf-8"):
                pass  # Create the empty __init__.py file

    def load_requirements(self) -> None:
        # Read and store dependencies from requirements.txt if it exists
        requirements_path: str = os.path.join(
            self.folder_path, "requirements.txt")
        if os.path.exists(requirements_path):
            with open(requirements_path, "r", encoding="utf-8") as f:
                self.requirements_txt = [line.strip()
                                         for line in f if line.strip()]

    def create_setup_file(self) -> None:
        # Check if a setup.py already exists in the original folder; if so,
        # copy it over
        existing_setup_path: str = os.path.join(self.folder_path, "setup.py")
        setup_file_path: str = os.path.join(
            self.project_spool_path, "setup.py")

        if os.path.exists(existing_setup_path):
            print(
                f"Found existing setup.py in {
                    self.folder_path}. Copying it to {
                    self.project_spool_path}."
            )
            shutil.copy(existing_setup_path, setup_file_path)
        else:
            # Generate a new setup.py if one does not exist in the original
            # folder
            print(
                f"No existing setup.py found in {
                    self.folder_path}. Creating a new setup.py."
            )

            setup_content: str = f"""
from setuptools import setup, find_packages

setup(
    name="{self.project_name}",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires={self.requirements_txt},
    entry_points={{
        'console_scripts': [
            '{self.project_name} = {self.project_name}.__main__:main',
        ],
    }},
)
            """
            with open(setup_file_path, "w", encoding="utf-8") as f:
                f.write(setup_content.strip())

    def spool(self) -> None:
        print(
            f"Setting up project structure for '{
                self.project_name}' in .spool/{
                self.project_name}"
        )
        self.setup_project_structure()
        print("Loading requirements...")
        self.load_requirements()
        print("Creating setup.py file...")
        self.create_setup_file()
        print(
            f"Project '{
                self.project_name}' prepared for installation at '.spool/{
                self.project_name}'."
        )
        print("To install, use:")
        print(f"% pip install .spool/{self.project_name}")


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Spool: Make a Python project installable.")
    parser.add_argument(
        "folder_path",
        help="Folder containing a Python script and optional requirements.txt")
    args: argparse.Namespace = parser.parse_args()

    Spooler(args.folder_path).spool()


if __name__ == "__main__":
    main()
