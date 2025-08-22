import os
import subprocess
import click
import shutil
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def check_lean_installation():
    """Check if Lean and Lake are properly installed."""
    try:
        result = subprocess.run(["lake", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return False, "Lake is installed but not working properly."
        return True, "Lake is properly installed."
    except FileNotFoundError:
        return False, "Lake not found. Please install Lean 4 from https://leanprover.github.io/lean4/doc/quickstart.html"
    except subprocess.TimeoutExpired:
        return False, "Lake command timed out. There may be an issue with your installation."
    except Exception as e:
        return False, f"Unexpected error checking Lake installation: {e}"

def validate_project_name(name):
    """Validate project name."""
    if not name:
        return False, "Project name cannot be empty."
    
    # Check for invalid characters
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', ' ']
    for char in invalid_chars:
        if char in name:
            return False, f"Project name cannot contain '{char}'."
    
    # Check if it starts with a letter or underscore
    if not (name[0].isalpha() or name[0] == '_'):
        return False, "Project name must start with a letter or underscore."
    
    return True, "Valid project name."

def create_project(name):
    """Creates a new Lean project using lake."""
    # Validate project name
    valid, msg = validate_project_name(name)
    if not valid:
        console.print(f"[red]Error: {msg}[/red]")
        return False
    
    # Check if directory exists
    project_path = Path(name)
    if project_path.exists():
        console.print(f"[red]Error: Directory '{name}' already exists.[/red]")
        return False
    
    # Check Lean installation
    lean_ok, lean_msg = check_lean_installation()
    if not lean_ok:
        console.print(f"[red]Error: {lean_msg}[/red]")
        return False

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"Creating Lean project '{name}'...", total=3)
        
        try:
            # Create directory
            progress.update(task, advance=1, description="Creating directory...")
            project_path.mkdir(parents=True, exist_ok=False)
            
            # Initialize Lean project
            progress.update(task, advance=1, description="Initializing Lean project...")
            result = subprocess.run(
                ["lake", "init", name, "math"], 
                cwd=project_path.parent,
                capture_output=True, 
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                # Clean up on failure
                shutil.rmtree(project_path, ignore_errors=True)
                error_msg = result.stderr or result.stdout or "Unknown error"
                console.print(f"[red]Error initializing project: {error_msg}[/red]")
                return False
            
            # Create a simple Main.lean file
            progress.update(task, advance=1, description="Creating example file...")
            main_file = project_path / name.capitalize() / "Basic.lean"
            main_file.parent.mkdir(exist_ok=True)
            main_file.write_text("-- Your Lean 4 code here\n\ndef hello := \"Hello from Lean 4!\"\n\n#eval hello\n")
            
            progress.update(task, completed=True)
            
            console.print(f"[green]✓ Successfully created project '{name}'[/green]")
            console.print(f"[blue]Next steps:[/blue]")
            console.print(f"  1. cd {name}")
            console.print(f"  2. lake build")
            console.print(f"  3. Edit {name.capitalize()}/Basic.lean")
            return True
            
        except subprocess.TimeoutExpired:
            shutil.rmtree(project_path, ignore_errors=True)
            console.print("[red]Error: Project initialization timed out.[/red]")
            return False
        except Exception as e:
            shutil.rmtree(project_path, ignore_errors=True)
            console.print(f"[red]Error creating project: {e}[/red]")
            return False