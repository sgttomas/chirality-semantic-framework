# Contributing to the Chirality Framework

First, thank you for considering contributing! This project is a direct, canonical implementation of the Chirality Framework algorithm, and we welcome contributions that refine, test, and document this core implementation.

## Core Philosophy: The "Semantic Calculator"

Please understand that this project is not a general-purpose, extensible framework. It is a **"semantic calculator"** designed to execute a fixed algorithm. Contributions should focus on improving the correctness, clarity, and observability of this algorithm, not on adding new framework features, plugins, or abstractions.

## Getting Started

### Prerequisites
- Python 3.9+
- An OpenAI API key (set as the `OPENAI_API_KEY` environment variable for live tests)

### Development Setup

```bash
# 1. Clone the repository
git clone <repository-url>
cd chirality-framework

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies, including development tools
pip install -e ".[dev]"

# 4. Run the offline test suite to verify setup
pytest
```

## How to Contribute

The most valuable contributions will be those that improve the core algorithm, its tests, or its documentation.

### Code Contributions

The core logic lives in `chirality/core/`.

*   **`operations.py`**: This is the heart of the calculator. It contains the `compute_cell_*` functions that implement the **Three-Stage Interpretation Pipeline**. If you are refining the algorithm, this is the primary file you will work in.
*   **`cell_resolver.py`**: This class is the sole interface to the LLM. Its `assemble_prompt` method is responsible for the dynamic, fragment-based prompt construction. Refinements to the prompting strategy happen here.
*   **`matrices.py`**: This file contains the canonical, fixed matrices (A, B, J). These should only be changed if the underlying Normative Specification of the Chirality Framework is updated.

### Testing Contributions

Our testing strategy is crucial for validating the calculator's correctness without making expensive LLM calls.

*   **Mock Resolver:** All core logic is tested against a `MockCellResolver` located in `tests/mocks.py`. This mock provides predictable, deterministic outputs.
*   **Adding Tests:** New tests for the core operations should be added to `tests/core/test_operations.py`. Please follow the existing structure, testing each stage of the pipeline independently before testing the end-to-end cell computation.

### Documentation Contributions

Clarity is essential. The two primary documents are:

*   **`README.md`**: The high-level project overview.
*   **`docs/ALGORITHM.md`**: The definitive technical description of the canonical algorithm and the 3-stage pipeline.

Improvements to these documents are highly welcome.

## Development Workflow

We follow a standard GitHub flow:

1.  Create a feature branch from `main` (e.g., `feature/refine-lensing-prompt`).
2.  Make your changes, including adding or updating tests.
3.  Ensure all tests pass (`pytest`).
4.  Update documentation if applicable.
5.  Submit a Pull Request to `main` with a clear description of your changes.

## Commit Message Convention

To maintain a clear and readable git history, this project follows the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification. Each commit message should be prefixed with a type that describes the change.

**Common Types:**
*   **feat:** A new feature or enhancement to the calculator's capabilities.
*   **fix:** A bug fix in the algorithm or its implementation.
*   **docs:** Changes to documentation (`.md` files, docstrings).
*   **test:** Adding new tests or correcting existing ones.
*   **refactor:** A code change that neither fixes a bug nor adds a feature.
*   **style:** Changes that do not affect the meaning of the code (white-space, formatting, etc).
*   **chore:** Changes to the build process or auxiliary tools.

**Example:**
```
feat(operations): Add compute_matrix_X function

This commit implements the next stage of the semantic valley, computing
the verification matrix [X] from [K] and [J].
```
