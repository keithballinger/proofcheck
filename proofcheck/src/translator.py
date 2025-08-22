import click
import re
from pathlib import Path
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Dict, List, Tuple, Optional

console = Console()

class LaTeXToLeanTranslator:
    """Translator for converting LaTeX mathematical expressions to Lean 4 syntax."""
    
    def __init__(self):
        # Basic symbol mappings
        self.symbol_map = {
            # Logic
            r"\\forall": "∀",
            r"\\exists": "∃",
            r"\\neg": "¬",
            r"\\land": "∧",
            r"\\lor": "∨",
            r"\\implies": "→",
            r"\\iff": "↔",
            r"\\Rightarrow": "→",
            r"\\Leftrightarrow": "↔",
            
            # Set theory
            r"\\in": "∈",
            r"\\notin": "∉",
            r"\\subset": "⊂",
            r"\\subseteq": "⊆",
            r"\\supset": "⊃",
            r"\\supseteq": "⊇",
            r"\\cup": "∪",
            r"\\cap": "∩",
            r"\\emptyset": "∅",
            r"\\setminus": "\\",
            
            # Relations
            r"\\leq": "≤",
            r"\\geq": "≥",
            r"\\neq": "≠",
            r"\\approx": "≈",
            r"\\equiv": "≡",
            r"\\sim": "∼",
            
            # Number sets
            r"\\mathbb{N}": "ℕ",
            r"\\mathbb{Z}": "ℤ",
            r"\\mathbb{Q}": "ℚ",
            r"\\mathbb{R}": "ℝ",
            r"\\mathbb{C}": "ℂ",
            r"\\N": "ℕ",
            r"\\Z": "ℤ",
            r"\\Q": "ℚ",
            r"\\R": "ℝ",
            r"\\C": "ℂ",
            
            # Greek letters
            r"\\alpha": "α",
            r"\\beta": "β",
            r"\\gamma": "γ",
            r"\\delta": "δ",
            r"\\epsilon": "ε",
            r"\\varepsilon": "ε",
            r"\\lambda": "λ",
            r"\\mu": "μ",
            r"\\pi": "π",
            r"\\sigma": "σ",
            r"\\tau": "τ",
            r"\\phi": "φ",
            r"\\varphi": "φ",
            r"\\psi": "ψ",
            r"\\omega": "ω",
            
            # Other symbols
            r"\\infty": "∞",
            r"\\partial": "∂",
            r"\\nabla": "∇",
            r"\\pm": "±",
            r"\\cdot": "·",
            r"\\times": "×",
            r"\\div": "÷",
            r"\\sum": "∑",
            r"\\prod": "∏",
            r"\\int": "∫",
        }
        
        # Environment mappings
        self.environment_map = {
            "theorem": "theorem",
            "lemma": "lemma",
            "proposition": "proposition",
            "corollary": "corollary",
            "definition": "def",
            "proof": "proof",
            "example": "example",
        }
    
    def translate_symbols(self, text: str) -> str:
        """Replace LaTeX symbols with Lean equivalents."""
        result = text
        for latex, lean in self.symbol_map.items():
            result = re.sub(latex, lean, result)
        return result
    
    def translate_functions(self, text: str) -> str:
        """Translate common mathematical functions."""
        # sin, cos, tan, log, exp, etc.
        functions = ["sin", "cos", "tan", "log", "exp", "ln", "sqrt", "abs"]
        for func in functions:
            # Replace \func{x} with func(x)
            pattern = rf"\\{func}\{{([^}}]*)\}}"
            result = re.sub(pattern, rf"{func}(\1)", text)
            # Replace \func x with func(x) for simple cases
            pattern = rf"\\{func}\s+([a-zA-Z0-9]+)"
            text = re.sub(pattern, rf"{func}(\1)", result)
        
        return text
    
    def translate_fractions(self, text: str) -> str:
        """Translate \\frac{a}{b} to (a) / (b)."""
        pattern = r"\\frac\{([^}]*)\}\{([^}]*)\}"
        return re.sub(pattern, r"(\1) / (\2)", text)
    
    def translate_superscripts(self, text: str) -> str:
        """Translate x^n to x^n (keep as is for simple cases)."""
        # For complex superscripts, wrap in parentheses
        pattern = r"\^{([^}]+)}"
        text = re.sub(pattern, r"^(\1)", text)
        # Simple superscripts stay as is
        return text
    
    def translate_subscripts(self, text: str) -> str:
        """Translate x_n to x₀, x₁, etc. for digits, or x_n for variables."""
        # Map digits to subscript unicode
        subscript_map = {
            "0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄",
            "5": "₅", "6": "₆", "7": "₇", "8": "₈", "9": "₉",
        }
        
        def replace_subscript(match):
            content = match.group(1)
            if content in subscript_map:
                return subscript_map[content]
            else:
                return f"_{content}"
        
        # Handle _{...}
        pattern = r"_\{([^}]+)\}"
        text = re.sub(pattern, replace_subscript, text)
        
        # Handle _x for single character
        pattern = r"_([a-zA-Z0-9])"
        text = re.sub(pattern, replace_subscript, text)
        
        return text
    
    def translate_sets(self, text: str) -> str:
        """Translate set notation {x | P(x)} to {x | P x}."""
        pattern = r"\{([^|]+)\|([^}]+)\}"
        return re.sub(pattern, r"{\1 | \2}", text)
    
    def translate_environments(self, text: str) -> str:
        """Translate LaTeX environments to Lean syntax."""
        result = []
        lines = text.split('\n')
        
        in_environment = None
        environment_content = []
        
        for line in lines:
            # Check for environment start
            begin_match = re.match(r"\\begin\{(\w+)\}(?:\[([^\]]*)\])?", line)
            if begin_match:
                env_name = begin_match.group(1)
                env_label = begin_match.group(2)
                
                if env_name in self.environment_map:
                    in_environment = env_name
                    environment_content = []
                    
                    # Start Lean construct
                    lean_construct = self.environment_map[env_name]
                    if env_label:
                        result.append(f"{lean_construct} {env_label} :")
                    else:
                        result.append(f"{lean_construct} :")
                else:
                    result.append(line)
                continue
            
            # Check for environment end
            end_match = re.match(r"\\end\{(\w+)\}", line)
            if end_match and in_environment:
                env_name = end_match.group(1)
                if env_name == in_environment:
                    # Process environment content
                    content = '\n'.join(environment_content)
                    if in_environment == "proof":
                        result.append("  by")
                        for content_line in environment_content:
                            result.append(f"    {content_line}")
                    else:
                        for content_line in environment_content:
                            result.append(f"  {content_line}")
                    
                    in_environment = None
                    environment_content = []
                continue
            
            # Collect environment content or add regular line
            if in_environment:
                environment_content.append(line)
            else:
                result.append(line)
        
        return '\n'.join(result)
    
    def translate_text_commands(self, text: str) -> str:
        """Remove or translate LaTeX text commands."""
        # Remove common LaTeX commands that don't translate
        commands_to_remove = [
            r"\\textbf\{([^}]*)\}",  # Bold text
            r"\\textit\{([^}]*)\}",  # Italic text
            r"\\emph\{([^}]*)\}",    # Emphasized text
            r"\\text\{([^}]*)\}",    # Regular text in math
        ]
        
        for pattern in commands_to_remove:
            text = re.sub(pattern, r"\1", text)
        
        # Remove labels and references
        text = re.sub(r"\\label\{[^}]*\}", "", text)
        text = re.sub(r"\\ref\{[^}]*\}", "(?)", text)
        
        return text
    
    def clean_latex_commands(self, text: str) -> str:
        """Remove remaining LaTeX commands that don't have direct translations."""
        # Remove document structure commands
        text = re.sub(r"\\documentclass.*\n", "", text)
        text = re.sub(r"\\usepackage.*\n", "", text)
        text = re.sub(r"\\begin\{document\}.*\n", "", text)
        text = re.sub(r"\\end\{document\}.*\n", "", text)
        text = re.sub(r"\\maketitle.*\n", "", text)
        text = re.sub(r"\\title\{[^}]*\}", "", text)
        text = re.sub(r"\\author\{[^}]*\}", "", text)
        text = re.sub(r"\\date\{[^}]*\}", "", text)
        
        # Remove section commands but keep titles as comments
        text = re.sub(r"\\section\{([^}]*)\}", r"-- Section: \1", text)
        text = re.sub(r"\\subsection\{([^}]*)\}", r"-- Subsection: \1", text)
        
        return text
    
    def translate(self, latex_text: str) -> str:
        """Main translation function."""
        # Apply translations in order
        result = latex_text
        
        # Clean LaTeX document structure
        result = self.clean_latex_commands(result)
        
        # Translate mathematical constructs
        result = self.translate_fractions(result)
        result = self.translate_functions(result)
        result = self.translate_superscripts(result)
        result = self.translate_subscripts(result)
        result = self.translate_sets(result)
        
        # Translate symbols
        result = self.translate_symbols(result)
        
        # Translate environments
        result = self.translate_environments(result)
        
        # Clean up text commands
        result = self.translate_text_commands(result)
        
        # Clean up extra whitespace
        result = re.sub(r"\n\n+", "\n\n", result)
        result = result.strip()
        
        return result

def validate_input_file(file_path: Path) -> Tuple[bool, str]:
    """Validate input file."""
    if not file_path.exists():
        return False, f"File not found: {file_path}"
    
    if not file_path.is_file():
        return False, f"Not a file: {file_path}"
    
    # Check file extension
    valid_extensions = ['.tex', '.txt', '.latex']
    if file_path.suffix.lower() not in valid_extensions:
        return False, f"Unsupported file type. Expected: {', '.join(valid_extensions)}"
    
    # Check file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    if file_path.stat().st_size > max_size:
        return False, "File too large (max 10MB)"
    
    return True, "Valid file"

def translate_file(input_path: str, output_path: Optional[str] = None):
    """Translate a LaTeX file to Lean 4."""
    input_file = Path(input_path)
    
    # Validate input
    valid, msg = validate_input_file(input_file)
    if not valid:
        console.print(f"[red]Error: {msg}[/red]")
        return False
    
    # Determine output path
    if output_path:
        output_file = Path(output_path)
    else:
        # Generate output filename
        output_file = input_file.with_suffix('.lean')
        if output_file == input_file:
            output_file = input_file.with_name(f"{input_file.stem}_translated.lean")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Translating LaTeX to Lean...", total=4)
        
        try:
            # Read input file
            progress.update(task, advance=1, description="Reading input file...")
            with open(input_file, 'r', encoding='utf-8') as f:
                latex_content = f.read()
            
            if not latex_content.strip():
                console.print("[yellow]Warning: Input file is empty.[/yellow]")
                return False
            
            # Translate
            progress.update(task, advance=1, description="Translating LaTeX to Lean...")
            translator = LaTeXToLeanTranslator()
            lean_content = translator.translate(latex_content)
            
            # Add header
            header = [
                "/-",
                f"  Translated from: {input_file.name}",
                "  Note: This is an automatic translation from LaTeX.",
                "  Manual review and adjustment may be required.",
                "-/",
                "",
                "-- Import common Lean libraries (adjust as needed)",
                "import Mathlib.Data.Real.Basic",
                "import Mathlib.Tactic",
                "",
                ""
            ]
            
            lean_content = '\n'.join(header) + lean_content
            
            # Write output file
            progress.update(task, advance=1, description="Writing output file...")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(lean_content)
            
            # Display result
            progress.update(task, advance=1, description="Complete!")
            
            console.print(f"[green]✓ Successfully translated to: {output_file}[/green]")
            
            # Show preview
            console.print("\n[blue]Preview of translated file:[/blue]")
            preview_lines = lean_content.split('\n')[:20]
            preview = '\n'.join(preview_lines)
            if len(lean_content.split('\n')) > 20:
                preview += "\n..."
            
            syntax = Syntax(preview, "lean", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title=str(output_file), border_style="blue"))
            
            return True
            
        except UnicodeDecodeError:
            console.print("[red]Error: File encoding issue. Please ensure the file is UTF-8 encoded.[/red]")
            return False
        except Exception as e:
            console.print(f"[red]Error during translation: {e}[/red]")
            return False

def latex_to_lean(latex_string: str) -> str:
    """Simple wrapper for backward compatibility."""
    translator = LaTeXToLeanTranslator()
    return translator.translate(latex_string)