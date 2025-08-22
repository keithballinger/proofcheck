# ProofCheck API Documentation

This document describes the internal API of ProofCheck for contributors and developers.

## Module Overview

### `src.cli`
Main entry point for the CLI application.

**Functions:**
- `cli()` - Main click group for all commands
- `new(project_name)` - Create a new Lean project
- `check(file_path)` - Check a Lean file
- `search(query)` - Search Mathlib
- `translate(input_path)` - Translate LaTeX to Lean
- `cache.*` - Cache management commands

### `src.lean`
Lean file checking and verification functionality.

**Classes:**
- `VerificationResult` - Result object for verification operations
  - `success: bool` - Whether verification succeeded
  - `message: str` - Result message

**Functions:**
- `check_lean_installation() -> Tuple[bool, str]` - Check if Lean/Lake are installed
- `find_project_root(path: str) -> Optional[str]` - Find Lean project root directory
- `check_file(file_path: str) -> VerificationResult` - Check a Lean file by building the project

### `src.project`
Project creation and management.

**Functions:**
- `check_lean_installation() -> Tuple[bool, str]` - Check Lake installation
- `validate_project_name(name: str) -> Tuple[bool, str]` - Validate project name
- `create_project(name: str) -> bool` - Create a new Lean project with Lake

### `src.search`
Mathlib search functionality.

**Functions:**
- `validate_query(query: str) -> Tuple[bool, str]` - Validate search query
- `format_search_results(data: Dict, query: str, max_results: int = 10)` - Format and display results
- `search_mathlib(query: str, timeout: int = 30, max_retries: int = 3, use_cache: bool = True) -> bool` - Search Mathlib

### `src.translator`
LaTeX to Lean translation.

**Classes:**
- `LaTeXToLeanTranslator` - Main translator class
  - `symbol_map: Dict[str, str]` - LaTeX to Lean symbol mappings
  - `environment_map: Dict[str, str]` - LaTeX environment mappings
  - `translate(latex_text: str) -> str` - Main translation method
  - `translate_symbols(text: str) -> str` - Replace LaTeX symbols
  - `translate_functions(text: str) -> str` - Translate mathematical functions
  - `translate_fractions(text: str) -> str` - Translate fractions
  - `translate_superscripts(text: str) -> str` - Handle superscripts
  - `translate_subscripts(text: str) -> str` - Handle subscripts
  - `translate_sets(text: str) -> str` - Translate set notation
  - `translate_environments(text: str) -> str` - Translate LaTeX environments

**Functions:**
- `validate_input_file(file_path: Path) -> Tuple[bool, str]` - Validate input file
- `translate_file(input_path: str, output_path: Optional[str] = None) -> bool` - Translate file
- `latex_to_lean(latex_string: str) -> str` - Simple translation wrapper

### `src.cache`
Caching functionality for search results.

**Classes:**
- `SearchCache` - File-based cache for search results
  - `__init__(cache_dir: Optional[Path] = None, ttl_seconds: int = 3600)` - Initialize cache
  - `get(query: str) -> Optional[Dict]` - Retrieve cached results
  - `set(query: str, data: Dict)` - Cache results
  - `clear() -> int` - Clear all cache entries
  - `clear_expired() -> int` - Clear expired entries
  - `get_cache_stats() -> Dict` - Get cache statistics

## Error Handling

All modules use consistent error handling:
- Return `False` or `None` for failures
- Use Rich console for error display
- Provide helpful error messages with recovery suggestions
- Handle timeouts, network errors, and file system issues gracefully

## Testing

Each module has corresponding tests in the `tests/` directory:
- `test_lean.py` - Tests for lean module
- `test_project.py` - Tests for project module  
- `test_search.py` - Tests for search module

Run tests with:
```bash
python -m pytest tests/ -v
```

## Contributing

When adding new features:

1. **Follow existing patterns** - Use Rich for output, return tuples for validation
2. **Add error handling** - Handle all exceptions gracefully
3. **Write tests** - Add unit tests for new functionality
4. **Update documentation** - Update this file and README
5. **Use type hints** - Add type hints to function signatures
6. **Validate inputs** - Always validate user inputs before processing

## Dependencies

Core dependencies:
- `click` - CLI framework
- `requests` - HTTP client for API calls
- `rich` - Terminal formatting and progress bars
- `pathlib` - File system operations

## Architecture Decisions

1. **Modular design** - Each command is in its own module
2. **Rich for UI** - Consistent, beautiful terminal output
3. **File-based cache** - Simple, portable caching solution
4. **Validation first** - Always validate before processing
5. **Progress indicators** - Show progress for long operations
6. **Graceful degradation** - Work without Lean installed where possible