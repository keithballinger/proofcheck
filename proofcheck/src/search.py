import requests
import click
import json
from urllib.parse import quote
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
import time

console = Console()

def validate_query(query):
    """Validate search query."""
    if not query or not query.strip():
        return False, "Search query cannot be empty."
    if len(query) > 500:
        return False, "Search query is too long (max 500 characters)."
    return True, "Valid query."

def format_search_results(data, query, max_results=10):
    """Format search results in a nice table."""
    hits = data.get('hits', [])
    
    if not hits:
        console.print("[yellow]No results found.[/yellow]")
        console.print("\n[dim]Tips:[/dim]")
        console.print("  • Try different keywords")
        console.print("  • Use more general terms")
        console.print("  • Check spelling")
        return
    
    # Create a table for results
    table = Table(title=f"Search Results for '{query}'", show_lines=True)
    table.add_column("Name", style="bright_blue", no_wrap=False)
    table.add_column("Type", style="green", no_wrap=False)
    table.add_column("Module", style="yellow")
    table.add_column("Documentation", style="dim", no_wrap=False, max_width=50)
    
    # Limit results
    displayed_hits = hits[:max_results]
    
    for hit in displayed_hits:
        name = hit.get('name', 'N/A')
        type_str = hit.get('type', 'N/A')
        module = hit.get('module', 'N/A')
        doc = hit.get('doc', '')
        
        # Truncate long documentation
        if doc and len(doc) > 100:
            doc = doc[:97] + "..."
        
        table.add_row(name, type_str, module, doc.strip() if doc else "")
    
    console.print(table)
    
    if len(hits) > max_results:
        console.print(f"\n[dim]Showing {max_results} of {len(hits)} results. Refine your search for more specific results.[/dim]")

def search_mathlib(query, timeout=30, max_retries=3):
    """Searches mathlib using the loogle.lean-lang.org API with error handling."""
    # Validate query
    valid, msg = validate_query(query)
    if not valid:
        console.print(f"[red]Error: {msg}[/red]")
        return False
    
    # URL encode the query
    encoded_query = quote(query)
    url = f"https://loogle.lean-lang.org/json?q={encoded_query}"
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"Searching Mathlib for '{query}'...", total=None)
        
        retry_count = 0
        while retry_count < max_retries:
            try:
                # Make request with timeout
                response = requests.get(url, timeout=timeout)
                
                # Check status code
                if response.status_code == 404:
                    progress.update(task, completed=True)
                    console.print("[yellow]Search service not available. Please try again later.[/yellow]")
                    return False
                
                response.raise_for_status()
                
                # Parse JSON
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    progress.update(task, completed=True)
                    console.print("[red]Error: Invalid response from search service.[/red]")
                    return False
                
                progress.update(task, completed=True)
                
                # Check for errors in response
                if data.get('error'):
                    console.print(f"[red]Search error: {data['error']}[/red]")
                    return False
                
                # Format and display results
                format_search_results(data, query)
                return True
                
            except requests.exceptions.Timeout:
                retry_count += 1
                if retry_count < max_retries:
                    progress.update(task, description=f"Request timed out. Retrying ({retry_count}/{max_retries})...")
                    time.sleep(2 ** retry_count)  # Exponential backoff
                else:
                    progress.update(task, completed=True)
                    console.print("[red]Error: Search request timed out. Please try again later.[/red]")
                    return False
                    
            except requests.exceptions.ConnectionError:
                progress.update(task, completed=True)
                console.print("[red]Error: Cannot connect to search service. Check your internet connection.[/red]")
                return False
                
            except requests.exceptions.RequestException as e:
                progress.update(task, completed=True)
                console.print(f"[red]Error connecting to search API: {e}[/red]")
                return False
        
        return False
