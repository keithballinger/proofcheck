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
NC='\033[0m' # No Color

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
    "proofcheck translate examples/basic_number_theory.tex"

run_command "Translate prime numbers theorems" \
    "proofcheck translate examples/prime_numbers.tex"

run_command "Translate set theory definitions" \
    "proofcheck translate examples/set_theory.tex"

echo -e "${GREEN}=== 2. Creating a New Lean Project ===${NC}"
echo ""

# Clean up if project exists from previous run
if [ -d "example_project" ]; then
    echo "Cleaning up previous example_project..."
    rm -rf example_project
fi

run_command "Create a new Lean project called 'example_project'" \
    "proofcheck new example_project"

echo -e "${GREEN}=== 3. Checking Lean Files ===${NC}"
echo ""

run_command "Check the translated number theory file" \
    "proofcheck check examples/basic_number_theory.lean"

echo -e "${BLUE}Note: The check might fail if the translation needs manual adjustments.${NC}"
echo -e "${BLUE}This is normal - LaTeX to Lean translation provides a starting point.${NC}"
echo ""
echo "Press Enter to continue..."
read

echo -e "${GREEN}=== 4. Searching Mathlib ===${NC}"
echo ""

run_command "Search for information about natural numbers" \
    "proofcheck search 'Nat.add'"

run_command "Search for prime number theorems" \
    "proofcheck search 'prime'"

run_command "Search for set theory definitions" \
    "proofcheck search 'Set.union'"

echo -e "${GREEN}=== 5. Cache Management ===${NC}"
echo ""

run_command "View cache statistics" \
    "proofcheck cache stats"

run_command "Search again to see cache in action" \
    "proofcheck search 'Nat.add'"

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
    "proofcheck check example_project/ExampleProject/Simple.lean"

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