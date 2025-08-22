#!/usr/bin/env python3
"""
ProofCheck MCP Server - Python implementation
Exposes ProofCheck functionality via Model Context Protocol
"""

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add proofcheck to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Import ProofCheck modules
try:
    from proofcheck.src.lean import check_file, check_lean_installation
    from proofcheck.src.project import create_project
    from proofcheck.src.search import search_mathlib
    from proofcheck.src.translator import translate_file, LaTeXToLeanTranslator
    from proofcheck.src.cache import SearchCache
except ImportError:
    print("Error: ProofCheck not found. Please install it first:", file=sys.stderr)
    print("  cd ../proofcheck && pip install -e .", file=sys.stderr)
    sys.exit(1)

# Create the MCP server
server = Server("proofcheck-mcp")

# Example Lean code templates
LEAN_EXAMPLES = """-- Example 1: Basic arithmetic
theorem add_zero (n : Nat) : n + 0 = n := by
  rfl

theorem zero_add (n : Nat) : 0 + n = n := by
  induction n with
  | zero => rfl
  | succ n ih => simp [Nat.succ_eq_add_one, ih]

-- Example 2: List operations
def reverse {α : Type} : List α → List α
  | [] => []
  | x :: xs => reverse xs ++ [x]

theorem reverse_reverse {α : Type} (xs : List α) : 
  reverse (reverse xs) = xs := by
  induction xs with
  | nil => rfl
  | cons x xs ih => sorry -- Exercise for the reader"""

LEAN_TEMPLATES = """-- Template for induction proof
theorem my_theorem (n : Nat) : P n := by
  induction n with
  | zero => 
    -- Base case
    sorry
  | succ n ih =>
    -- Inductive step
    -- ih : P n
    -- Goal: P (n + 1)
    sorry

-- Template for equality proof
theorem equality_proof (x y : α) (h : x = y) : f x = f y := by
  rw [h]

-- Template for contradiction proof
theorem by_contradiction (p : Prop) : p := by
  by_contra h
  -- h : ¬p
  -- Goal: False
  sorry"""

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """List available resources."""
    return [
        types.Resource(
            uri="lean://examples",
            name="Example Lean Files",
            description="Collection of example Lean proofs and definitions",
            mimeType="text/plain",
        ),
        types.Resource(
            uri="lean://templates",
            name="Lean Templates",
            description="Template files for common proof patterns",
            mimeType="text/plain",
        ),
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read a resource by URI."""
    if uri == "lean://examples":
        return LEAN_EXAMPLES
    elif uri == "lean://templates":
        return LEAN_TEMPLATES
    else:
        raise ValueError(f"Unknown resource: {uri}")

@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """List available prompts."""
    return [
        types.Prompt(
            name="formalize_statement",
            description="Help formalize a mathematical statement in Lean",
            arguments=[
                types.PromptArgument(
                    name="statement",
                    description="The mathematical statement to formalize",
                    required=True,
                )
            ],
        ),
        types.Prompt(
            name="prove_theorem",
            description="Guide through proving a theorem step by step",
            arguments=[
                types.PromptArgument(
                    name="theorem",
                    description="The theorem to prove",
                    required=True,
                ),
                types.PromptArgument(
                    name="approach",
                    description="Preferred proof approach (induction, contradiction, etc.)",
                    required=False,
                ),
            ],
        ),
        types.Prompt(
            name="debug_proof",
            description="Help debug a failing Lean proof",
            arguments=[
                types.PromptArgument(
                    name="code",
                    description="The Lean code with the failing proof",
                    required=True,
                ),
                types.PromptArgument(
                    name="error",
                    description="The error message from Lean",
                    required=True,
                ),
            ],
        ),
    ]

@server.get_prompt()
async def handle_get_prompt(
    name: str, arguments: Optional[Dict[str, str]] = None
) -> types.GetPromptResult:
    """Generate a prompt based on the template."""
    if not arguments:
        arguments = {}
    
    if name == "formalize_statement":
        statement = arguments.get("statement", "")
        return types.GetPromptResult(
            description=f"Formalize: {statement}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"""I need help formalizing this mathematical statement in Lean 4:

"{statement}"

Please:
1. Identify the key mathematical concepts involved
2. Suggest appropriate Lean types and definitions
3. Write the formal Lean statement
4. Explain any assumptions or simplifications made"""
                    ),
                )
            ],
        )
    
    elif name == "prove_theorem":
        theorem = arguments.get("theorem", "")
        approach = arguments.get("approach", "")
        approach_text = f" using {approach}" if approach else ""
        
        return types.GetPromptResult(
            description=f"Prove: {theorem}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"""I need help proving this theorem in Lean 4{approach_text}:

{theorem}

Please:
1. Analyze what needs to be proven
2. Identify useful lemmas from Mathlib
3. Outline the proof strategy
4. Provide the complete Lean proof with explanations
5. Suggest alternative approaches if applicable"""
                    ),
                )
            ],
        )
    
    elif name == "debug_proof":
        code = arguments.get("code", "")
        error = arguments.get("error", "")
        
        return types.GetPromptResult(
            description="Debug Lean proof",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"""My Lean proof is failing with an error. Please help me fix it.

Code:
```lean
{code}
```

Error:
```
{error}
```

Please:
1. Explain what the error means
2. Identify the issue in the code
3. Provide a corrected version
4. Explain the fix and why it works
5. Suggest how to avoid similar errors"""
                    ),
                )
            ],
        )
    
    else:
        raise ValueError(f"Unknown prompt: {name}")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="translate_latex",
            description="Translate LaTeX mathematical content to Lean 4 syntax",
            inputSchema={
                "type": "object",
                "properties": {
                    "latex_content": {
                        "type": "string",
                        "description": "LaTeX content to translate",
                    },
                    "save_to_file": {
                        "type": "boolean",
                        "description": "Whether to save the output to a file",
                        "default": False,
                    },
                },
                "required": ["latex_content"],
            },
        ),
        types.Tool(
            name="create_lean_project",
            description="Create a new Lean 4 project with Lake",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "Name of the new Lean project",
                    },
                },
                "required": ["project_name"],
            },
        ),
        types.Tool(
            name="check_lean_file",
            description="Check a Lean file for correctness by building the project",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the Lean file to check",
                    },
                },
                "required": ["file_path"],
            },
        ),
        types.Tool(
            name="search_mathlib",
            description="Search Lean Mathlib for theorems and definitions",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for Mathlib",
                    },
                    "use_cache": {
                        "type": "boolean",
                        "description": "Whether to use cached results",
                        "default": True,
                    },
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="check_lean_installation",
            description="Check if Lean 4 and Lake are properly installed",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Optional[Dict[str, Any]] = None
) -> list[types.TextContent]:
    """Execute a tool and return the result."""
    if not arguments:
        arguments = {}
    
    try:
        if name == "translate_latex":
            latex_content = arguments.get("latex_content", "")
            save_to_file = arguments.get("save_to_file", False)
            
            # Create translator
            translator = LaTeXToLeanTranslator()
            lean_content = translator.translate(latex_content)
            
            # Optionally save to file
            output_path = ""
            if save_to_file:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.lean', delete=False) as f:
                    f.write(lean_content)
                    output_path = f.name
            
            result = f"Translation successful!\n\nLean code:\n```lean\n{lean_content}\n```"
            if output_path:
                result += f"\n\nSaved to: {output_path}"
            
            return [types.TextContent(type="text", text=result)]
        
        elif name == "create_lean_project":
            project_name = arguments.get("project_name", "")
            
            if not project_name or "/" in project_name:
                return [types.TextContent(
                    type="text",
                    text="Error: Invalid project name"
                )]
            
            success = create_project(project_name)
            
            if success:
                result = f"""Created Lean project '{project_name}'.

Next steps:
1. cd {project_name}
2. Edit {project_name.capitalize()}/Basic.lean
3. Use 'proofcheck check' to verify your proofs"""
            else:
                result = f"Failed to create project '{project_name}'. Check if Lean is installed."
            
            return [types.TextContent(type="text", text=result)]
        
        elif name == "check_lean_file":
            file_path = arguments.get("file_path", "")
            
            if not Path(file_path).exists():
                return [types.TextContent(
                    type="text",
                    text=f"Error: File not found: {file_path}"
                )]
            
            result = check_file(file_path)
            
            return [types.TextContent(type="text", text=str(result))]
        
        elif name == "search_mathlib":
            query = arguments.get("query", "")
            use_cache = arguments.get("use_cache", True)
            
            if not query:
                return [types.TextContent(
                    type="text",
                    text="Error: Query is required"
                )]
            
            # Note: This returns True/False, not the actual results
            # We'd need to modify search_mathlib to return results instead of printing
            success = search_mathlib(query, use_cache=use_cache)
            
            if success:
                result = f"Search completed for: {query}"
            else:
                result = f"Search failed for: {query}"
            
            return [types.TextContent(type="text", text=result)]
        
        elif name == "check_lean_installation":
            is_installed, message = check_lean_installation()
            
            if is_installed:
                result = "✓ Lean 4 and Lake are properly installed"
            else:
                result = f"✗ {message}"
            
            return [types.TextContent(type="text", text=result)]
        
        else:
            return [types.TextContent(
                type="text",
                text=f"Error: Unknown tool: {name}"
            )]
    
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]

async def main():
    """Run the MCP server."""
    # Run the server using stdin/stdout
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="proofcheck-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())