import json
import sys
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

import click
import pytest

# Absolute imports instead of relative ones
from openergo.graph import graph as _graph
from openergo.python_executor import PythonExecutor
from openergo.quality import quality_check as _quality
from openergo.spooler import Spooler


class CommandGroup:
    """Encapsulates handlers and command configuration."""

    @staticmethod
    def graph_handler(path: List[str], routingkey: List[str]) -> None:
        """Handler for the `graph` command."""
        _graph(path, routingkey)
        click.echo(f"Graph called with path={path} and routingkey={routingkey}")

    @staticmethod
    def quality_handler() -> None:
        """Handler for the `quality` command."""
        _quality()  # Hardcoded fail_fast=False
        click.echo("Quality called")

    @staticmethod
    def spool_handler(folder_path: str) -> None:
        """Handler for the `spool` command."""
        click.echo(f"Spooling project from {folder_path}...")
        spooler: Spooler = Spooler(folder_path)
        spooler.spool()
        click.echo(f"Spooling project from {folder_path}...")

    @staticmethod
    def run_handler(config_file: str, args: Optional[List[str]]) -> None:
        """Handler for the `run` command."""
        try:
            # Specify encoding explicitly when opening files
            with open(config_file, "r", encoding="utf-8") as file:
                config: Dict[str, Any] = json.load(file)

            procedure_path: str = config["shell"]["procedure"]
            result: str = PythonExecutor(procedure_path, config).execute()
            click.echo(f"Executing procedure at {procedure_path} with args={args}")
            # Placeholder logic
            # result: str = f"Result of {procedure_path} with args {args}"
            click.echo(f"Executor result: {result}")

        except FileNotFoundError as e:
            click.echo(f"File not found: {e}", err=True)
        except json.JSONDecodeError as e:
            click.echo(f"Error parsing JSON: {e}", err=True)
        except IOError as e:  # For handling I/O related errors
            click.echo(f"IO Error: {e}", err=True)

    # Command configuration as a dictionary
    COMMANDS: Dict[str, Dict[str, Any]] = {
        "graph": {
            "options": [
                click.argument("path", nargs=-1),
                click.option(
                    "-r", "--routingkey", multiple=True, required=True, help="Collection elements for routingkeys"
                ),
            ],
            "handler": graph_handler,  # Referencing static method directly
        },
        "spool": {
            "options": [
                click.argument("folder_path", type=click.Path(exists=True, file_okay=False, dir_okay=True)),
            ],
            "handler": spool_handler,  # Referencing static method directly
        },
        "quality": {
            "options": [],
            "handler": quality_handler,  # Referencing static method directly
        },
        "run": {
            "options": [
                click.argument("config_file", type=click.Path(exists=True, file_okay=True, dir_okay=False)),
                click.option("-a", "--args", multiple=True, help="Arguments to be passed to the executor"),
            ],
            "handler": run_handler,  # Referencing static method directly
        },
    }


def run_tests() -> None:
    """Run tests with coverage before executing any command."""
    click.echo("Running tests with coverage...")
    result: int = pytest.main(
        [
            "./tests",  # Path to tests
            "--quiet",  # Suppress detailed test output
            "--cov=openergo",  # Measure coverage for the 'openergo' package
            "--cov-report=term-missing",  # Show missing lines in the terminal
        ]
    )
    if result != 0:
        click.echo("Tests failed. Exiting.", err=True)
        sys.exit(result)


def with_quality_check(handler: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to enforce running quality check before a command,
    except for the 'quality' command itself.
    """

    @wraps(handler)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Skip quality check if the command is 'quality'
        if "quality" in sys.argv:
            return handler(*args, **kwargs)

        # Run quality check before executing the command
        _quality(fail_fast=False)
        return handler(*args, **kwargs)

    return wrapper


@click.group()
@click.version_option(version="1.0")
def main() -> None:
    """Main CLI group."""


def register_commands(command_config: Dict[str, Dict[str, Any]]) -> None:
    """Dynamically register commands from configuration."""
    for name, config in command_config.items():
        options: List[Any] = config["options"]
        handler: Callable[..., Any] = config["handler"]

        # Create the command dynamically
        def make_command(handler: Callable[..., Any], name: str) -> Callable[..., Any]:
            @main.command(name=name)
            @wraps(handler)
            def cli_function(*args: Any, **kwargs: Any) -> Any:
                wrapped_handler = with_quality_check(handler)
                # return wrapped_handler(*args, **kwargs)
                return handler(*args, **kwargs)

            return cli_function

        cli_function: Callable[..., Any] = make_command(handler, name)

        # Apply options dynamically
        for option in reversed(options):
            cli_function = option(cli_function)


# Register all commands from the CommandGroup configuration
register_commands(CommandGroup.COMMANDS)


if __name__ == "__main__":
    main()
