
import click
from .cli_classes import StdioCLI, AmqpCLI, EventloopCLI, GraphCLI

@click.group()
def main():
    """Main entry point for the openergo CLI."""
    pass

@main.command()
@click.argument("config_file", type=click.Path(exists=True))
def stdio(config_file):
    """Handle stdio protocol."""
    cli = StdioCLI(config_file)
    cli.handle()

@main.command()
@click.argument("config_file", type=click.Path(exists=True))
def amqp(config_file):
    """Handle amqp protocol."""
    cli = AmqpCLI(config_file)
    cli.handle()

@main.command()
@click.argument("config_file", type=click.Path(exists=True))
def eventloop(config_file):
    """Handle eventloop protocol."""
    cli = EventloopCLI(config_file)
    cli.handle()

@main.command()
@click.option('--config', '-c', type=click.Path(exists=True), help="Path to configuration file.")
@click.option('--routing-key', '-r', multiple=True, help="Specify one or more routing keys.")
def graph(config, routing_key):
    """Handle the graph protocol with optional config and routing keys."""
    cli = GraphCLI(config_file=config, routing_keys=routing_key)
    cli.handle()

if __name__ == "__main__":
    main()
