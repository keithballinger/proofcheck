import click
from .project import create_project
from .lean import check_file as check_file_command
from .search import search_mathlib
from .translator import translate_file as translate_file_command
from .cache import SearchCache
from rich.console import Console

console = Console()

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

@cli.group()
def cache():
    """Manage the search cache."""
    pass

@cache.command('clear')
def cache_clear():
    """Clear all cached search results."""
    search_cache = SearchCache()
    count = search_cache.clear()
    console.print(f"[green]✓ Cleared {count} cache entries[/green]")

@cache.command('stats')
def cache_stats():
    """Show cache statistics."""
    search_cache = SearchCache()
    stats = search_cache.get_cache_stats()
    
    console.print("[bold]Cache Statistics[/bold]")
    console.print(f"  Location: {stats['cache_directory']}")
    console.print(f"  Total entries: {stats['total_entries']}")
    console.print(f"  Valid entries: {stats['valid_entries']}")
    console.print(f"  Expired entries: {stats['expired_entries']}")
    console.print(f"  Total size: {stats['total_size_bytes']:,} bytes")
    console.print(f"  TTL: {stats['ttl_seconds']} seconds")

@cache.command('clean')
def cache_clean():
    """Remove expired cache entries."""
    search_cache = SearchCache()
    count = search_cache.clear_expired()
    console.print(f"[green]✓ Removed {count} expired cache entries[/green]")