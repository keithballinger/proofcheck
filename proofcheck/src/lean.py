import subprocess
import click
import os

class VerificationResult:
    def __init__(self, success, message):
        self.success = success
        self.message = message

    def __str__(self):
        if self.success:
            return click.style(self.message, fg='green')
        else:
            return click.style(self.message, fg='red')

def find_project_root(path):
    """Finds the project root by looking for lakefile.lean."""
    current_dir = os.path.abspath(path)
    while True:
        if 'lakefile.toml' in os.listdir(current_dir):
            return current_dir
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            return None # Reached the filesystem root
        current_dir = parent_dir

def check_file(file_path):
    """Checks a Lean project by building it with lake."""
    click.echo(f"Checking file: {file_path}")
    
    project_root = find_project_root(os.path.dirname(file_path))
    if not project_root:
        return VerificationResult(False, "Error: Could not find project root (no lakefile.lean found).")

    click.echo(f"Found project root: {project_root}")
    try:
        # Run lake build from the project root
        result = subprocess.run(["lake", "build"], cwd=project_root, check=True, capture_output=True, text=True)
        return VerificationResult(True, "✓ Project built successfully! All proofs verified.")
    except FileNotFoundError:
        return VerificationResult(False, "Error: `lake` command not found.\nPlease install Lean first.")
    except subprocess.CalledProcessError as e:
        return VerificationResult(False, f"✗ Build failed:\n{e.stderr}")
