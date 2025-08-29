# The Chirality Framework (CF14) Canonical Algorithm

## 1. Overview & Philosophy: The "Semantic Calculator"

The Chirality Framework is implemented as a fixed algorithm, not a flexible platform. Its purpose is to function as a "semantic calculator," taking canonical, unchanging inputs (Matrices A and B) and executing a deterministic sequence of operations to produce a series of insightful, structured outputs (Matrices C, F, D, etc.).

The core design principles are:
- **Simplicity Over Abstraction:** The code is a direct translation of the algorithm.
- **Directness Over Indirection:** The flow of control is linear and explicit.
- **Observability is Paramount:** The process is designed to be fully transparent through detailed tracing and a cell-first CLI.

## 2. The Canonical Matrices

The algorithm begins with two fixed, axiomatic matrices. The authoritative source for these matrices is the code itself, located in `chirality/core/matrices.py`. These definitions are based on the final normative specification (14.2.1.1).

*   **`MATRIX_A` (3x4): The Problem Statement Matrix.** Defines the ontological axes for Normative, Operative, and Evaluative perspectives against Guiding, Applying, Judging, and Reviewing functions.
*   **`MATRIX_B` (4x4): The Decision Basis Matrix.** Defines the ontological axes for levels of knowledge (Data, Information, Knowledge, Wisdom) against logical attributes (Necessity, Sufficiency, Completeness, Consistency).
*   **`MATRIX_J` (3x4): The Judgment Matrix.** A truncated version of Matrix B, used in later stages.

## 3. The Core Algorithm: The Three-Stage Interpretation Pipeline

The "secret sauce" of the Chirality Framework is the process by which new meaning is generated for a cell at a specific matrix coordinate `(i, j)`. This is a three-stage pipeline:

### Stage 1: Combinatorial (Mechanical)
This stage is purely mechanical and does not involve an LLM. It combines the terms from the input matrices according to the specified operation (e.g., for a dot product, it generates all the `A[i,k] * B[k,j]` word pairs).

*   **Input:** Raw terms from source matrices.
*   **Output:** A list of string pairs (e.g., `["Direction * Essential Facts", "Implementation * Critical Context", ...]`).

### Stage 2: Semantic Resolution (First Meaning Layer)
An LLM resolves each raw word pair from Stage 1 into a single, concise concept. This is the first layer of meaning generation.

*   **Input:** A single word pair (e.g., `"Direction * Essential Facts"`).
*   **Output:** A resolved concept (e.g., `"Guiding Imperatives"`).

### Stage 3: Ontological Lensing (Deep Interpretation)
The resolved concepts from Stage 2 are combined and then interpreted by an LLM through the powerful contextual lens of the cell's ontological coordinates (its row and column labels). The normative specification clarifies this is a sequential process: first the column lens is applied, then the row lens, and finally the perspectives are synthesized.

*   **Input:** The combined concepts and the ontological context (e.g., `content: "Guiding Imperatives, Applied Context..."`, `row_lens: "Normative"`, `col_lens: "Necessity (vs Contingency)"`).
*   **Output:** A final, synthesized narrative that explains the meaning of the content within that specific ontological context.

## 4. Sequence of Operations

The calculator performs the following sequence of operations, with each step building on the last:

1.  **Compute Matrix C (Requirements):** `C = A * B`
    *   Each cell `C(i,j)` is computed using the full 3-stage pipeline on the dot product of row `i` from `A` and column `j` from `B`.
2.  **Compute Matrix F (Functions):** `F = J ⊙ C`
    *   Each cell `F(i,j)` is computed using an element-wise multiplication of `J(i,j)` and `C(i,j)`, which is then processed through the Semantic Resolution and Lensing stages.
3.  **Synthesize Matrix D (Solution Objectives):** `D = A + F`
    *   Each cell `D(i,j)` is computed by mechanically synthesizing a statement from `A(i,j)` and `F(i,j)` using a fixed formula, which is then processed through the Lensing stage.

## 5. Observability

The entire process is designed to be transparent.
*   **CLI:** Use the `compute-cell` command with the `--verbose` flag to see the input and output of all three stages for any cell.
*   **Tracing:** Use the `--trace` flag to generate a detailed JSONL file in the `traces/` directory, which contains a complete, machine-readable record of every stage of every cell computation.
