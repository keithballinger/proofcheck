import os
import subprocess
import click

def create_project(name):
    """Creates a new Lean project using lake."""
    if os.path.exists(name):
        click.echo(f"Error: Directory '{name}' already exists.", err=True)
        return

    try:
        click.echo(f"Creating directory and initializing new Lean project '{name}'...")
        os.makedirs(name)
        # Run lake init from within the new directory
        subprocess.run(["lake", "init", ".", "math"], cwd=name, check=True, capture_output=True, text=True)
        click.echo(f"Successfully created project '{name}'.")
        click.echo(f"To get started, run: cd {name}")
    except FileNotFoundError:
        click.echo("Error: `lake` command not found.", err=True)
        click.echo("Please install Lean and the `lake` build tool first.", err=True)
    except subprocess.CalledProcessError as e:
        click.echo(f"Error initializing Lean project:", err=True)
        click.echo(e.stderr, err=True)