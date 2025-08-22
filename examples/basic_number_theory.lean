/-
  Translated from: basic_number_theory.tex
  Note: This is an automatic translation from LaTeX.
  Manual review and adjustment may be required.
-/

-- Import common Lean libraries (adjust as needed)
import Mathlib.Data.Real.Basic
import Mathlib.Tactic

-- Section: Natural Numbers

theorem Addition Commutativity :
  For all natural numbers $n, m ∈ ℕ$, we have $n + m = m + n$.

proof :
  by
    By induction on $n$.

theorem Zero Identity :
  For all $n ∈ ℕ$, we have $n + 0 = n$ and $0 + n = n$.

lemma Successor Addition :
  For all $n, m ∈ ℕ$, we have $succ(n) + m = succ(n + m)$.

-- Section: Divisibility

def :
  We say that $a$ divides $b$ (written $a \mid b$) if there exists $k ∈ ℕ$ such that $b = a · k$.

theorem Divisibility Transitivity :
  If $a \mid b$ and $b \mid c$, then $a \mid c$.

proof :
  by
    Suppose $a \mid b$ and $b \mid c$. Then there exist $k₁, k₂ ∈ ℕ$ such that $b = a · k₁$ and $c = b · k₂$. 
    Therefore, $c = (a · k₁) · k₂ = a · (k₁ · k₂)$, so $a \mid c$.

\end{document}