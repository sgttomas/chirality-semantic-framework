# Agent Protocol for the Chirality Framework

**Version:** 15.0.0

## 1. Core Philosophy for AI Agents

Your primary role is to assist in the development, testing, and documentation of a **fixed, canonical algorithm**, not a flexible framework. The project is a "semantic calculator" with a deterministic, three-stage interpretation pipeline at its core. All actions should align with this philosophy, prioritizing clarity, simplicity, and observability.

## 2. Primary Development Tasks

Your work will focus on the core components of the semantic calculator.

### Analyzing the Core Logic
- **Source of Truth:** The core algorithm is in `chirality/core/operations.py`. When analyzing the logic, focus on the `compute_cell_*` functions and their implementation of the 3-stage pipeline (Combinatorial -> Semantic Resolution -> Lensing).
- **Prompting Engine:** The `chirality/core/cell_resolver.py` is the sole interface to the LLM. Its `assemble_prompt` method is key to how context is passed to the LLM.
- **Canonical Data:** The fixed input matrices are defined as constants in `chirality/core/matrices.py`.

### Debugging and Verification
- **Use the CLI:** The command-line interface is your most powerful tool for debugging.
  ```bash
  # Verify the output of a single cell
  python -m chirality.cli compute-cell C --i 0 --j 0

  # See the full 3-stage pipeline for a cell
  python -m chirality.cli compute-cell C --i 0 --j 0 --verbose
  ```
- **Use the Tracer:** For detailed, machine-readable logs, run commands with the `--trace` flag. The output will be in the `traces/` directory.

### Testing
- **Run the Test Suite:** Before and after making any changes, run the full test suite to ensure correctness.
  ```bash
  # Run all offline unit tests from the project root
  pytest
  ```
- **Writing New Tests:** New tests should be added to `tests/core/test_operations.py`. Use the `MockCellResolver` from `tests/mocks.py` to test algorithmic logic without making live LLM calls.

## 3. Documentation Tasks

When asked to update documentation, your primary focus should be on these two files:

- **`README.md`**: The high-level introduction to the "semantic calculator."
- **`docs/ALGORITHM.md`**: The definitive technical reference for the 3-stage pipeline and canonical matrices.

Ensure all documentation accurately reflects the current, simplified architecture.
