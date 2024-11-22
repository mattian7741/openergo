import json
import sys
from functools import wraps

import click
import pytest

# Absolute imports instead of relative ones
from openergo.graph import graph as _graph
from openergo.python_executor import PythonExecutor
from openergo.quality import quality_check as _quality
from openergo.spooler import Spooler


@click.group()
@click.version_option(version="1.0")
def main():
    """Main CLI group."""


def with_quality_check(handler):
    """
    Decorator to enforce running quality check before a command,
    only if the '-q' flag is used.
    """

    @wraps(handler)
    def wrapper(*args, **kwargs):
        # Fetch the value of the 'q' flag from kwargs
        q = kwargs.get('q', False)
        # Run the quality check only if 'q' flag is True
        if q:
            _quality(fail_fast=False)
        return handler(*args, **kwargs)

    return wrapper


@click.command()
@click.argument("path", nargs=-1)
@click.option("-r", "--routingkey", multiple=True, required=True,
              help="Collection elements for routingkeys")
# Add the '-q' flag
@click.option("-q", is_flag=True, help="Enable quality check")
@with_quality_check
def graph(path, routingkey, q):
    """Handler for the `graph` command."""
    _graph(path, routingkey)
    click.echo(f"Graph called with path={path} and routingkey={routingkey}")


@click.command()
@click.argument("folder_path", type=click.Path(exists=True,
                file_okay=False, dir_okay=True))
# Add the '-q' flag
@click.option("-q", is_flag=True, help="Enable quality check")
@with_quality_check
def spool(folder_path, q):
    """Handler for the `spool` command."""
    click.echo(f"Spooling project from {folder_path}...")
    spooler = Spooler(folder_path)
    spooler.spool()
    click.echo(f"Spooling project from {folder_path}...")


@click.command()
def quality():
    """Handler for the `quality` command."""
    _quality(fail_fast=False)  # Hardcoded fail_fast=False for this command
    click.echo("Quality called")


@click.command()
@click.argument("config_file", type=click.Path(exists=True,
                file_okay=True, dir_okay=False))
@click.option("-a", "--args", multiple=True,
              help="Arguments to be passed to the executor")
# Add the '-q' flag
@click.option("-q", is_flag=True, help="Enable quality check")
@with_quality_check
def run(config_file, args, q):
    """Handler for the `run` command."""
    try:
        with open(config_file, "r", encoding="utf-8") as file:
            config = json.load(file)

        procedure_path = config["shell"]["procedure"]
        for result in PythonExecutor(procedure_path, config).execute(
            *[json.loads(arg) for arg in args]):            
            click.echo(f"Executing procedure at {procedure_path} with args={args}")
            click.echo(f"Executor result: {result}")

    except FileNotFoundError as e:
        click.echo(f"File not found: {e}", err=True)
    # except json.JSONDecodeError as e:
    #     print(e)
    #     click.echo(f"Error parsing JSON: {e}", err=True)
    except IOError as e:
        click.echo(f"IO Error: {e}", err=True)


def run_tests():
    """Run tests with coverage before executing any command."""
    click.echo("Running tests with coverage...")
    result = pytest.main(
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


# Registering the commands to the main group
main.add_command(graph)
main.add_command(spool)
main.add_command(quality)  # No decorator needed for 'quality'
main.add_command(run)


if __name__ == "__main__":
    run_tests()  # Run tests before executing commands
    main()
