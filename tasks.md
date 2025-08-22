# ProofCheck CLI: Development Task Plan

This document outlines the tasks required to build the ProofCheck CLI tool. The plan is divided into phases, each focusing on a specific set of features.

## Phase 1: Core Project Setup and the `new` Command

**Goal:** Establish the development environment and implement the first user-facing command to create new projects.

*   **Task 1.1: Setup Python Project Structure**
    *   Create the `proofcheck/` directory.
    *   Create `proofcheck/src/` for the main source code.
    *   Create `tests/` for unit tests.

*   **Task 1.2: Set up Dependencies**
    *   Create a `requirements.txt` file.
    *   Add `click` to `requirements.txt`.
    *   Provide instructions for setting up a virtual environment.

*   **Task 1.3: Implement the CLI Entry Point**
    *   Create `proofcheck/src/cli.py` with the main `cli` group from `click`.
    *   Create `proofcheck/src/__main__.py` to make the package executable.

*   **Task 1.4: Implement the `new` Command**
    *   Add the `new` command to `cli.py`.
    *   Create `proofcheck/src/project.py` to house the project creation logic.
    *   The `create_project` function in `project.py` will call `lake init <name> math` as a subprocess.

*   **Task 1.5: Add Error Handling to `new`**
    *   Handle the case where `lake` is not installed (e.g., `FileNotFoundError`).
    *   Handle the case where a project directory with the same name already exists.
    *   Handle errors from the `lake` subprocess itself.

*   **Task 1.6: Write Unit Tests for `new`**
    *   Create `tests/test_project.py`.
    *   Write a test that checks if the `new` command successfully creates a directory.
    *   Use mocking (`unittest.mock`) to simulate the `subprocess.run` call to `lake`, so the tests don't depend on `lake` being installed.

## Phase 2: The `check` Command

**Goal:** Implement the core functionality of the tool: validating a Lean proof file.

*   **Task 2.1: Implement the `check` command**
    *   Add the `check` command to `cli.py`.
    *   It will take a file path as an argument.

*   **Task 2.2: Implement the Lean Process Manager**
    *   Create `proofcheck/src/lean.py`.
    *   Implement a `check_file` function that runs `lean <file_path>` in a subprocess.

*   **Task 2.3: Implement Output Parsing**
    *   In `lean.py`, parse the `stdout` and `stderr` from the `lean` process.
    *   Distinguish between successful checks, proof errors, and system errors.
    *   Create a simple data class to return the result (e.g., `VerificationResult(success: bool, message: str)`).

*   **Task 2.4: Write Unit Tests for `check`**
    *   Create `tests/test_lean.py`.
    *   Create mock `.lean` files (one correct, one with a syntax error, one with a proof error).
    *   Write tests that call `check_file` on these mock files and assert that the results are parsed correctly (again, using mocking for the subprocess call).

## Phase 3: The `search` Command

**Goal:** Add the ability to search for existing theorems in Mathlib.

*   **Task 3.1: Implement the `search` command**
    *   Add the `search` command to `cli.py`.

*   **Task 3.2: Implement the Search Service**
    *   Create `proofcheck/src/search.py`.
    *   Implement a `search_mathlib` function that queries a public API (e.g., `loogle.lean-lang.org`).
    *   Use the `requests` library for HTTP calls (add to `requirements.txt`).

*   **Task 3.3: Format Search Results**
    *   Parse the JSON response from the API and display it in a user-friendly format in the CLI.

*   **Task 3.4: Write Unit Tests for `search`**
    *   Create `tests/test_search.py`.
    *   Use mocking to simulate the HTTP request to the search API.

## Phase 4: Packaging and Distribution

**Goal:** Make the tool easy to install and run for end-users.

*   **Task 4.1: Create `pyproject.toml`**
    *   Create and configure `pyproject.toml` to define the project metadata and dependencies.
    *   Define the entry point for the `proofcheck` command.

*   **Task 4.2: Write Installation Instructions**
    *   Update the `README.md` (or create a new `INSTALL.md`) with clear instructions on how to install the tool using `pip`.
