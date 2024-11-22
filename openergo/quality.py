import subprocess
import sys
from typing import List, Tuple


def quality_check(mod: str = "./openergo", fail_fast: bool = True) -> None:
    """
    Run code quality checks, linting, and tests on the given module.

    Args:
        mod: Path to the module to check (default: './openergo').
        fail_fast: If True, stop on the first failure. If False, continue running all checks even if they fail.
    """
    steps: List[Tuple[str, str]] = [
        (
            f"autopep8 --in-place --aggressive --recursive {mod}",
            "Formatting code (autopep8)"),
        (f"black -S --line-length 120 {mod}", "Formatting code (black)"),
        (f"isort {mod}", "Sorting imports (isort)"),
        (
            f"mypy --strict --implicit-reexport --explicit-package-bases --ignore-missing-imports {mod}",
            "Type Checking (mypy)",
        ),
        (f"flake8 --ignore=E501 {mod}",
         "Linting (flake8, ignoring line-too-long errors)"),
        (
            f"pylint {mod} --disable=missing-docstring,empty-docstring,line-too-long,too-few-public-methods,too-many-public-methods",
            "Linting (pylint)",
        ),
        (f"pytest --cov={mod} --cov-report=term-missing",
         "Running unit tests (pytest)"),
        (f"radon cc {mod} -a -nc --min=B",
         "Complexity check (radon, enforcing A grade)"),
    ]

    for command, description in steps:
        run_command(command, description, fail_fast)

    print("\033[32mAll checks passed successfully.\033[0m")


def run_command(command: str, description: str, fail_fast: bool) -> None:
    """
    Run a shell command with a description.
    Exit the script if the command fails (if fail_fast is True).

    Args:
        command: Shell command to execute.
        description: Description of the action being performed.
        fail_fast: If True, exit on failure. If False, continue even if the command fails.
    """
    print(f"\033[1m{description}...\033[0m")
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(
            f"\033[31m{description} failed with return code {
                e.returncode}. {
                'Aborting.' if fail_fast else 'Continuing.'}\033[0m"
        )
        if fail_fast:
            sys.exit(e.returncode)
