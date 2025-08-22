# ProofCheck CLI: Product Architecture & Technical Design

## 1. Overview and Guiding Principles

This document outlines the technical architecture for the `ProofCheck` command-line interface (CLI). The primary goal is to create a robust, user-friendly, and extensible tool that acts as a bridge between a user's mathematical text and the powerful Lean 4 proof assistant.

### Guiding Principles:

*   **Lean as the Core Engine:** We will not reinvent proof checking. The system is an abstraction layer over the `lean` executable. Our primary job is to manage projects and files, and to invoke the `lean` process correctly.
*   **Developer Experience is Key:** The tool should be intuitive for users who are mathematicians or computer scientists, but not necessarily experts in formal methods. Error messages should be clear and helpful.
*   **Extensibility:** The architecture must be modular to support future enhancements, such as a GUI, integration with other provers, or advanced translation features.
*   **Convention over Configuration:** We will use a standard project structure and build process, based on Lean's own tooling (`lake`), to minimize the need for user configuration.

## 2. High-Level Architecture

The system follows a layered architecture.

```mermaid
graph TD
    A[User (CLI)] --> B{Presentation Layer (Click)};
    B --> C{Application Logic Layer};
    C --> D[Project Manager];
    C --> E[Lean Process Manager];
    C --> F[Search Service];
    C --> G[Translator Service];
    D --> H[File System];
    E --> I[Lean 4 Executable];
    F --> J[Mathlib Search API];
    G --> K[LaTeX Parsing Library];
```

### Layers:

1.  **Presentation Layer:** The user-facing CLI, built using a modern Python framework. It is responsible for parsing commands and arguments, and for formatting and displaying output.
2.  **Application Logic Layer:** The central orchestrator. It receives commands from the Presentation Layer and delegates tasks to the appropriate service or manager.
3.  **Service & Manager Layer:**
    *   **Project Manager:** Handles the creation and management of `ProofCheck` projects (which are essentially Lean projects).
    *   **Lean Process Manager:** The most critical component. It is responsible for invoking the `lean` executable with the correct arguments, managing the subprocess, and parsing its output (`stdout`, `stderr`).
    *   **Search Service:** Implements the logic for searching the Lean Mathlib library.
    *   **Translator Service:** (Future) Implements the logic for translating LaTeX to Lean.
4.  **Backend/External Layer:**
    *   **File System:** Standard file operations.
    *   **Lean 4 Executable:** The external `lean` process that we invoke.
    *   **External APIs:** Web services for searching Mathlib or other tasks.

## 3. Technology Stack

*   **Language:** Python 3.10+
*   **CLI Framework:** `click` - For its excellent support for composable commands, automatic help generation, and rich formatting.
*   **Backend Prover:** Lean 4
*   **Lean Project Management:** `lake` (Lean's build tool)
*   **Process Interaction:** Python's `subprocess` module.
*   **Configuration Files:** `lakefile.lean` (for Lean) and potentially a `proofcheck.toml` in the future for project-level configuration.
*   **LaTeX Parsing:** `pylatexenc` - A robust library for parsing LaTeX.

## 4. Component Deep-Dive

### 4.1. Presentation Layer (`cli.py`)

*   Uses `@click.group` to define the main `proofcheck` command.
*   Each subcommand (`new`, `check`, etc.) is a separate function decorated with `@proofcheck.command()`.
*   Responsible for all `print()` or `echo()` calls to the console.
*   Handles user-facing error messages (e.g., "Error: File not found").

### 4.2. Project Manager (`project.py`)

*   **`create_project(name)`:**
    1.  Creates the root directory (`./<name>`).
    2.  Executes `lake init <name>` within that directory. This is the standard way to create a new Lean project and it automatically generates the `lakefile.lean`, `lean-toolchain`, and a basic `src/Main.lean`.
    3.  Potentially adds a `.gitignore` file with common Lean build artifacts (`build/`, `deps/`).
*   **`find_project_root()`:**
    *   Traverses up from the current directory, looking for a `lakefile.lean` or `lean-toolchain` file to identify the project root. This allows users to run `proofcheck` commands from subdirectories.

### 4.3. Lean Process Manager (`lean.py`)

*   **`check_file(file_path)`:**
    1.  Constructs the command: `lean <file_path>`.
    2.  Uses `subprocess.run()` to execute the command.
    3.  **Crucially**, it captures `stdout` and `stderr`.
    4.  **Output Parsing:**
        *   If `stderr` is empty and the exit code is 0, the check is successful.
        *   If `stderr` contains content, it indicates a proof error. The manager will parse this output to extract the line number, column, and error message for user-friendly display. Lean's error messages are structured, which will aid in parsing.
*   **`build_project()`:**
    *   Executes `lake build`. This is used to ensure all dependencies are up-to-date before running checks.

### 4.4. Search Service (`search.py`)

*   **`search_mathlib(query)`:**
    1.  Makes an HTTP GET request to the `loogle.lean-lang.org` API (or a similar service).
    2.  The query is URL-encoded.
    3.  Parses the JSON response from the API.
    4.  Formats the results (e.g., theorem name, type signature) for display in the CLI.
    5.  Includes a fallback to a local `grep`-like search if the API is unavailable.

## 5. Core Workflow Analysis: `proofcheck check <file>`

This is the most important workflow.

1.  **User Input:** `proofcheck check src/parity.lean`
2.  **CLI Layer (`cli.py`):**
    *   The `check` command function is invoked with `file = "src/parity.lean"`.
    *   It calls `app.logic.check_file("src/parity.lean")`.
3.  **App Logic Layer (`app.py`):**
    *   Calls `project.find_project_root()` to locate the project's root directory.
    *   Calls `lean.check_file(absolute_path_to_file)`.
4.  **Lean Process Manager (`lean.py`):**
    *   `subprocess.run(["lean", "/path/to/project/src/parity.lean"], capture_output=True, text=True)`
    *   The `lean` process starts. It loads the file, imports dependencies, and type-checks the definitions and proofs.
    *   **Success Case:** Lean exits with code 0. `stderr` is empty. The function returns a `Result(success=True, output=stdout)`.
    *   **Failure Case:** Lean finds an error. It writes a formatted error message to `stderr` and exits with a non-zero code. The function returns `Result(success=False, error=stderr)`.
5.  **Back to App Logic:**
    *   The logic layer receives the `Result` object.
6.  **Back to Presentation Layer:**
    *   If `success` is `True`, it prints a simple success message.
    *   If `success` is `False`, it parses the `error` string and prints a formatted, user-friendly error message, potentially with syntax highlighting.

## 6. Data Models and File Structures

### Project Structure (generated by `lake init`):

```
my_project/
├── .git/
├── .gitignore
├── lakefile.lean       # Lean build configuration
├── lean-toolchain      # Specifies the exact Lean version
└── src/
    └── Main.lean       # Main source file
```

### Configuration:

*   Lean configuration is handled entirely by `lakefile.lean` and `lean-toolchain`. We will not introduce a separate `proofcheck.toml` unless absolutely necessary, to adhere to the "Convention over Configuration" principle.

## 7. Extensibility and Roadmap

*   **Translator Service:** The `Translator` class will be designed to be pluggable. Initially, it will support LaTeX, but in the future, we could add support for Markdown, AsciiMath, etc.
*   **Pluggable Provers:** The `LeanProcessManager` will be an implementation of a generic `ProverManager` abstract base class. In the future, we could add `CoqProcessManager` or `IsabelleProcessManager` and allow the user to choose the backend in a configuration file.
*   **GUI:** A future GUI (perhaps using a web framework like Flask/React or a desktop framework like Qt) would interact with the Application Logic Layer directly, bypassing the CLI layer. The modular design makes this straightforward.
