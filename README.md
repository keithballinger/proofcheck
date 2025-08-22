# ProofCheck

A command-line tool for formalizing and validating mathematical proofs using Lean 4.

## Prerequisites

- Python 3.8 or higher
- Lean 4 (install from https://leanprover.github.io/lean4/doc/quickstart.html)

## Installation

### From Source

1. Clone the repository:
```bash
git clone https://github.com/keithballinger/proofcheck.git
cd proofcheck
```

2. Install the ProofCheck CLI:
```bash
cd proofcheck
pip install -e .
```

This will install the `proofcheck` command globally.

## Usage

### Create a New Lean Project

```bash
proofcheck new my_proof_project
cd my_proof_project
```

This creates a new Lean 4 project with the necessary configuration files.

### Check a Lean File

Verify that your Lean proofs are correct:

```bash
proofcheck check src/Main.lean
```

### Search Mathlib

Search for theorems and definitions in Lean's mathematical library:

```bash
proofcheck search "prime number"
```

### Translate LaTeX to Lean

Convert mathematical statements from LaTeX format to Lean 4:

```bash
proofcheck translate proof.tex
```

## Commands

- `proofcheck new <project_name>` - Create a new Lean project
- `proofcheck check <file_path>` - Verify a Lean file
- `proofcheck search <query>` - Search Mathlib for theorems
- `proofcheck translate <tex_file>` - Convert LaTeX to Lean

## Development

To run tests:

```bash
python -m pytest tests/
```

## MCP Server (AI Assistant Integration)

ProofCheck includes an MCP (Model Context Protocol) server that allows AI assistants like Claude to use ProofCheck tools directly.

### Quick Setup

1. Install the MCP server dependencies:
```bash
pip install mcp
```

2. Add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "proofcheck": {
      "command": "python3",
      "args": ["/absolute/path/to/science_buddy/mcp/proofcheck_mcp.py"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/science_buddy"
      }
    }
  }
}
```

3. Restart Claude Desktop

Now you can ask Claude to:
- "Translate this LaTeX theorem to Lean"
- "Create a new Lean project"
- "Search Mathlib for prime number theorems"
- "Help me debug this Lean proof"

See `mcp/README.md` for full MCP documentation.

## License

MIT
