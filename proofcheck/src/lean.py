import subprocess
import click
import os
import shutil
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

class VerificationResult:
    def __init__(self, success, message):
        self.success = success
        self.message = message

    def __str__(self):
        if self.success:
            return click.style(self.message, fg='green')
        else:
            return click.style(self.message, fg='red')
    
    def __bool__(self):
        return self.success

def check_lean_installation():
    """Check if Lean and Lake are properly installed."""
    try:
        # Check for lake
        result = subprocess.run(["lake", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return False, "Lake is installed but not working properly."
        
        # Check for lean
        result = subprocess.run(["lean", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return False, "Lean is installed but not working properly."
        
        return True, "Lean and Lake are properly installed."
    except FileNotFoundError:
        return False, "Lean/Lake not found. Please install Lean 4 from https://leanprover.github.io/lean4/doc/quickstart.html"
    except subprocess.TimeoutExpired:
        return False, "Lean/Lake commands timed out. There may be an issue with your installation."
    except Exception as e:
        return False, f"Unexpected error checking Lean installation: {e}"

def find_project_root(path):
    """Finds the project root by looking for lakefile.toml or lakefile.lean."""
    try:
        current_path = Path(path).resolve()
        
        # If path is a file, start from its directory
        if current_path.is_file():
            current_path = current_path.parent
        
        # Search up the directory tree
        for parent in [current_path] + list(current_path.parents):
            if (parent / "lakefile.toml").exists() or (parent / "lakefile.lean").exists():
                return str(parent)
        
        return None
    except Exception as e:
        console.print(f"[red]Error finding project root: {e}[/red]")
        return None

def check_file(file_path):
    """Checks a Lean file by building the project with lake."""
    # Validate file path
    file_path = Path(file_path)
    if not file_path.exists():
        return VerificationResult(False, f"Error: File not found: {file_path}")
    
    if not str(file_path).endswith('.lean'):
        return VerificationResult(False, "Error: File must be a .lean file")
    
    # Check Lean installation
    lean_ok, lean_msg = check_lean_installation()
    if not lean_ok:
        return VerificationResult(False, f"Error: {lean_msg}")
    
    console.print(f"[blue]Checking file:[/blue] {file_path}")
    
    # Find project root
    project_root = find_project_root(file_path)
    if not project_root:
        return VerificationResult(False, "Error: Could not find project root (no lakefile.toml or lakefile.lean found).\nMake sure you're in a Lean project directory.")

    console.print(f"[blue]Project root:[/blue] {project_root}")
    
    # Check if it's a single file or full project build
    relative_path = file_path.relative_to(project_root) if file_path.is_absolute() else file_path
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Building project...", total=None)
        
        try:
            # Run lake build from the project root
            result = subprocess.run(
                ["lake", "build"], 
                cwd=project_root, 
                capture_output=True, 
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            progress.update(task, completed=True)
            
            if result.returncode == 0:
                return VerificationResult(True, "✓ Project built successfully! All proofs verified.")
            else:
                # Parse error output for better formatting
                error_output = result.stderr or result.stdout
                return VerificationResult(False, f"✗ Build failed:\n{error_output}")
                
        except subprocess.TimeoutExpired:
            progress.update(task, completed=True)
            return VerificationResult(False, "Error: Build timed out after 5 minutes.")
        except FileNotFoundError:
            progress.update(task, completed=True)
            return VerificationResult(False, "Error: `lake` command not found.\nPlease install Lean 4 first.")
        except Exception as e:
            progress.update(task, completed=True)
            return VerificationResult(False, f"Error: Unexpected error during build: {e}")
