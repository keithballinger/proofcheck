#!/bin/bash

# ProofCheck Examples Demo Script
# This script demonstrates how to use ProofCheck with the example files

set -e  # Exit on error

echo "================================================"
echo "        ProofCheck Examples Demo"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Detect how to run proofcheck
PROOFCHECK_CMD=""

# Method 1: Check if proofcheck is installed as a command
if command -v proofcheck &> /dev/null; then
    PROOFCHECK_CMD="proofcheck"
    echo -e "${GREEN}✓ Found installed proofcheck command${NC}"
# Method 2: Try to run as Python module from project directory
elif [ -f "proofcheck/src/cli.py" ]; then
    # Check if Python is available
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}Error: Python not found${NC}"
        exit 1
    fi
    
    PROOFCHECK_CMD="$PYTHON_CMD -m proofcheck.src.cli"
    echo -e "${YELLOW}Running ProofCheck as Python module (not installed)${NC}"
    echo -e "${BLUE}To install ProofCheck globally, run:${NC}"
    echo "  cd proofcheck && pip install -e ."
else
    echo -e "${RED}Error: ProofCheck not found!${NC}"
    echo ""
    echo "Please either:"
    echo "1. Install ProofCheck:"
    echo "   cd proofcheck"
    echo "   pip install -e ."
    echo ""
    echo "2. Or run this script from the project root directory"
    echo "   where the 'proofcheck' folder exists"
    exit 1
fi

echo ""

# Function to run a command with description
run_command() {
    local description="$1"
    local command="$2"
    
    echo -e "${BLUE}→ ${description}${NC}"
    echo -e "${YELLOW}  \$ ${command}${NC}"
    echo ""
    eval "$command"
    echo ""
    echo "Press Enter to continue..."
    read
    echo ""
}

# Check if we're in the right directory
if [ ! -f "examples/basic_number_theory.tex" ]; then
    echo -e "${YELLOW}Please run this script from the project root directory${NC}"
    echo "Usage: ./examples/run_examples.sh"
    exit 1
fi

echo -e "${GREEN}=== 1. Translating LaTeX to Lean ===${NC}"
echo ""

run_command "Translate basic number theory from LaTeX to Lean" \
    "$PROOFCHECK_CMD translate examples/basic_number_theory.tex"

run_command "Translate prime numbers theorems" \
    "$PROOFCHECK_CMD translate examples/prime_numbers.tex"

run_command "Translate set theory definitions" \
    "$PROOFCHECK_CMD translate examples/set_theory.tex"

echo -e "${GREEN}=== 2. Creating a New Lean Project ===${NC}"
echo ""

# Clean up if project exists from previous run
if [ -d "example_project" ]; then
    echo "Cleaning up previous example_project..."
    rm -rf example_project
fi

run_command "Create a new Lean project called 'example_project'" \
    "$PROOFCHECK_CMD new example_project"

echo -e "${GREEN}=== 3. Checking Lean Files ===${NC}"
echo ""

run_command "Check the translated number theory file" \
    "$PROOFCHECK_CMD check examples/basic_number_theory.lean"

echo -e "${BLUE}Note: The check might fail if the translation needs manual adjustments.${NC}"
echo -e "${BLUE}This is normal - LaTeX to Lean translation provides a starting point.${NC}"
echo ""
echo "Press Enter to continue..."
read

echo -e "${GREEN}=== 4. Searching Mathlib ===${NC}"
echo ""

run_command "Search for information about natural numbers" \
    "$PROOFCHECK_CMD search 'Nat.add'"

run_command "Search for prime number theorems" \
    "$PROOFCHECK_CMD search 'prime'"

run_command "Search for set theory definitions" \
    "$PROOFCHECK_CMD search 'Set.union'"

echo -e "${GREEN}=== 5. Cache Management ===${NC}"
echo ""

run_command "View cache statistics" \
    "$PROOFCHECK_CMD cache stats"

run_command "Search again to see cache in action" \
    "$PROOFCHECK_CMD search 'Nat.add'"

echo -e "${BLUE}Notice the 'Using cached results' message above${NC}"
echo ""

echo -e "${GREEN}=== 6. Working with the Created Project ===${NC}"
echo ""

cat > example_project/ExampleProject/Simple.lean << 'EOF'
-- A simple Lean 4 file to demonstrate proofcheck

theorem add_zero (n : Nat) : n + 0 = n := by
  rfl

theorem zero_add (n : Nat) : 0 + n = n := by
  induction n with
  | zero => rfl
  | succ n ih => simp [Nat.succ_eq_add_one, ih]

#eval add_zero 5
EOF

echo "Created example_project/ExampleProject/Simple.lean with simple theorems"
echo ""

run_command "Check our simple theorems file" \
    "$PROOFCHECK_CMD check example_project/ExampleProject/Simple.lean"

echo -e "${GREEN}=== Demo Complete! ===${NC}"
echo ""
echo "Summary of what we did:"
echo "1. Translated LaTeX files to Lean using 'proofcheck translate'"
echo "2. Created a new Lean project using 'proofcheck new'"
echo "3. Checked Lean files using 'proofcheck check'"
echo "4. Searched Mathlib using 'proofcheck search'"
echo "5. Viewed cache statistics using 'proofcheck cache stats'"
echo "6. Created and verified custom Lean proofs"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "- Edit the translated .lean files to fix any issues"
echo "- Explore the example_project directory"
echo "- Try translating your own LaTeX files"
echo "- Use 'proofcheck --help' to see all available commands"
echo ""

# Cleanup option
echo -e "${YELLOW}Do you want to clean up the generated files? (y/n)${NC}"
read -r cleanup

if [[ "$cleanup" == "y" || "$cleanup" == "Y" ]]; then
    echo "Cleaning up..."
    rm -f examples/*.lean
    rm -rf example_project
    echo "Cleanup complete!"
else
    echo "Generated files kept for further exploration:"
    echo "  - examples/*.lean (translated files)"
    echo "  - example_project/ (Lean project)"
fi