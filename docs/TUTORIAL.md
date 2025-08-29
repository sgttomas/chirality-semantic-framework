# Tutorial: From Axioms to Objectives

This tutorial demonstrates the end-to-end process of the Chirality Framework's "semantic calculator." We will walk through the generation of the first three matrices (C, F, and D), showing how the system transforms high-level, abstract axioms into concrete, actionable objectives.

This example uses the normative case, where the problem being solved is "generating reliable knowledge."

## Step 1: The Setup - Canonical Matrices

The process begins with two fixed inputs, defined in `chirality/core/matrices.py`:

*   **`MATRIX_A` (Problem Statement):** Defines the perspectives (Normative, Operative, Evaluative) and functions (Guiding, Applying, etc.) of the problem space.
*   **`MATRIX_B` (Decision Basis):** Defines the levels of knowledge (Data, Information, etc.) and logical attributes (Necessity, Sufficiency, etc.).

## Step 2: Computing Matrix C (Requirements)

The first operation is `C = A * B`. This generates the core requirements. Let's trace the creation of a single cell, **C(0,0)**, which is at the intersection of the "Normative" row and the "Necessity (vs Contingency)" column.

### The 3-Stage Pipeline for C(0,0)

**Stage 1: Combinatorial (Mechanical)**

The system first mechanically computes the dot product for C(0,0), which involves combining four pairs of terms. No LLM is used here.

*   **Input:** `A(0,0...3)` and `B(0...3,0)`
*   **Output (raw k-products):**
    *   `"Direction" * "Essential Facts"`
    *   `"Implementation" * "Critical Context"`
    *   `"Evaluation" * "Fundamental Understanding"`
    *   `"Assessment" * "Vital Judgment"`

**Stage 2: Semantic Resolution (First Meaning)**

Next, the LLM is asked to find the semantic intersection of each pair, one by one.

*   **Input:** `"Direction" * "Essential Facts"`
*   **Output:** `"Guiding Imperatives"`

This is repeated for all four pairs, resulting in a list of resolved concepts:
`["Guiding Imperatives", "Applied Context", "Core Evaluation Criteria", "Critical Assessment"]`

**Stage 3: Ontological Lensing (Deep Insight)**

Finally, the resolved concepts are combined and interpreted through the powerful lens of the cell's coordinates.

*   **Input:**
    *   **Content:** `"Guiding Imperatives, Applied Context, Core Evaluation Criteria, Critical Assessment"`
    *   **Row Lens:** `"Normative"`
    *   **Column Lens:** `"Necessity (vs Contingency)"`
*   **Output (Final Cell Value):** A synthesized narrative, such as: `"To generate reliable knowledge, it is imperative to establish guiding principles based on essential facts and apply them within a critical context, ensuring that core evaluation criteria are used to make a decisive final assessment."`

This process is repeated for all 12 cells, resulting in the complete **Matrix C**.

## Step 3: Computing Matrices F and D (Objectives)

The process continues in the "Objectives" station:

1.  **Matrix F is computed** using an element-wise multiplication: `F = J ⊙ C`. Each cell `F(i,j)` is the semantic resolution of the terms from `J(i,j)` and `C(i,j)`, which is then passed through the Lensing stage.
2.  **Matrix D is synthesized** using the formula `D = A + F`. Each cell `D(i,j)` is created by mechanically combining the terms from `A(i,j)` and `F(i,j)` into a sentence, which is then passed through the Lensing stage to generate a final, actionable objective.

## Conclusion

Through this structured, observable, and repeatable process, the Chirality Framework successfully transforms a set of abstract, axiomatic inputs into a rich set of concrete requirements and objectives. The 3-stage pipeline ensures that meaning is generated in a traceable and contextually relevant way at every step of the semantic valley journey.
