import requests
import click

def search_mathlib(query):
    """Searches mathlib using the loogle.lean-lang.org API."""
    click.echo(f"Searching for: {query}")
    try:
        response = requests.get(f"https://loogle.lean-lang.org/json?q=\"{query}\"")
        response.raise_for_status() # Raise an exception for bad status codes
        data = response.json()
        if not data.get('hits'):
            click.echo("No results found.")
            return

        for hit in data['hits']:
            click.echo("-" * 20)
            click.echo(click.style(hit.get('name', 'N/A'), fg='bright_blue'))
            click.echo(f"  Type: {hit.get('type', 'N/A')}")
            if hit.get('doc'):
                click.echo(f"  Doc: {hit.get('doc').strip()}")

    except requests.exceptions.RequestException as e:
        click.echo(f"Error connecting to search API: {e}", err=True)
