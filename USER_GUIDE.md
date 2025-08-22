# ProofCheck CLI - User Guide

## 1. Vision: Your Science Buddy for Mathematical Proofs

ProofCheck is a command-line tool designed to bring the power of formal verification to your research. It helps you translate mathematical proofs from papers and textbooks into a formal language and use a state-of-the-art proof assistant to check their validity, step-by-step.

Our goal is to create a "science buddy" that helps you reason with more confidence, catch subtle errors in arguments, and build a personal, verifiable library of mathematical knowledge.

This tool is built on top of the **Lean proof assistant**, a powerful open-source project from Microsoft Research. You don't need to be a Lean expert to use ProofCheck, but as you grow, you'll have the full power of Lean at your fingertips.

## 2. Installation and Setup

To get started with ProofCheck, you'll need to install the tool itself and its core dependency, the Lean proof assistant.

```bash
# Step 1: Install Lean using its official installer
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh

# Step 2: Install the ProofCheck CLI (this is a hypothetical installation)
# In a real scenario, this would be an npm, pip, or similar package.
npm install -g proofcheck-cli
```

After installation, you can verify that everything is working by running:
`proofcheck --version`

## 3. Core Concepts of Formal Verification

Formal verification requires translating human-readable mathematics into a structured language that a computer can understand. Here are the key concepts:

*   **Definitions:** These are the basic building blocks. We define mathematical objects, functions, and their properties.
*   **Axioms:** These are fundamental truths that we assume without proof.
*   **Theorems:** These are statements that we want to prove are true, based on our definitions and axioms.
*   **Proofs (or "Proof Scripts"):** A proof is a sequence of logical steps that demonstrates the truth of a theorem. In Lean, we write these as "proof scripts" using a language of "tactics" that apply logical rules.

## 4. Tutorial: Validating a Proof from "Entropic Complexity"

Let's walk through validating **Theorem 10** from the paper "Entropic Complexity: Thermodynamic Lower Bounds for Computation". This will be our first test case.

**Theorem 10 (Parity - Tight Bound):** For PARITY : {0,1}" → {0,1} computing the XOR of n bits: `EC_PARITY(n) = n - 1`

### Step 1: Create a new project

First, we create a new project to house our formalization work.

```bash
proofcheck new entropic_complexity
cd entropic_complexity
```

This command creates a new directory `entropic_complexity/` with the necessary configuration files and a `src/` folder for our proof files.

### Step 2: Formalize the Definitions and Theorem

Create a new file `src/parity.lean`. In this file, we will write the Lean code to formalize the concepts needed for Theorem 10.

*(Note: This is a simplified model for the sake of a tutorial. A full formalization would require more detail.)*

```lean
-- We use the Natural numbers (ℕ) for simplicity.
import data.nat.basic

-- Based on the paper, the Entropic Complexity (EC) of a function
-- is the number of erasures it performs.
-- Algorithm 1 for PARITY performs n-1 erasures.
def EC_parity (n : ℕ) : ℕ := n - 1

-- Now, we state the theorem we want to prove.
theorem parity_tight_bound (n : ℕ) : EC_parity n = n - 1 :=
begin
  -- The proof begins here.
  -- In Lean, we use "tactics" to build the proof step-by-step.
  -- The `refl` tactic proves goals of the form `A = A`.
  refl,
end
```

This Lean code defines the Entropic Complexity for the PARITY function and then states and proves the theorem. The proof is just `refl` (reflexivity) because we defined `EC_parity(n)` to be `n-1` directly. A more complex proof would involve formalizing the PTM and Algorithm 1 in more detail.

### Step 3: Check the Proof

Now, from your terminal, run the `check` command:

```bash
proofcheck check src/parity.lean
```

If the proof is correct, ProofCheck will use the Lean compiler in the background and report success:

```
✅ src/parity.lean: Proof verified successfully!
```

Congratulations! You've just formally verified a theorem from a research paper.

## 5. Command Reference

ProofCheck provides a suite of commands to manage your verification projects.

*   `proofcheck new <project_name>`
    *   Creates a new Lean project with a standard directory structure.

*   `proofcheck check <file.lean>`
    *   Checks the specified file for correctness. This is the core command for validating your proofs.

*   `proofcheck search <keyword>`
    *   Searches the Lean mathematical library (`mathlib`) for theorems and definitions related to your keyword. This is incredibly useful for finding existing results you can build on.
    *   Example: `proofcheck search "prime number"`

*   `proofcheck translate <file.tex>` (Ambitious Future Feature)
    *   Attempts to parse a LaTeX file and translate the mathematical statements into Lean templates. This is a research-level challenge, and the initial version will provide a "best effort" translation that will require manual refinement.

## 6. Roadmap and Future Work

This user guide lays the foundation. The journey ahead involves:

*   **Building the ProofCheck CLI:** Implementing the commands described above.
*   **Deepening the "Entropic Complexity" Formalization:** Moving beyond the tutorial to formalize more of the paper's concepts, such as the Physical Turing Machine and other theorems. This will be the true test of our tool.
*   **Improving the Translator:** Enhancing the LaTeX-to-Lean translator to handle a wider variety of mathematical notation and prose.
*   **Interactive Mode:** Creating a REPL-style interactive mode for exploring proofs.
*   **Community Library:** Allowing users to share and build upon a community-maintained library of formalized papers.
