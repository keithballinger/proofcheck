import click
from .project import create_project
from .lean import check_file as check_file_command
from .search import search_mathlib
from .translator import translate_file as translate_file_command

@click.group()
def cli():
    """A CLI tool to help formalize and validate mathematical proofs using Lean."""
    pass

@cli.command()
@click.argument('project_name')
def new(project_name):
    """Creates a new ProofCheck project."""
    create_project(project_name)

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
def check(file_path):
    """Checks a Lean file for correctness."""
    result = check_file_command(file_path)
    if result:
        click.echo(result)

@cli.command()
@click.argument('query')
def search(query):
    """Searches the Lean Mathlib for a given query."""
    search_mathlib(query)

@cli.command()
@click.argument('input_path', type=click.Path(exists=True, dir_okay=False))
def translate(input_path):
    """Translates a text file with LaTeX into a Lean file."""
    translate_file_command(input_path)