"""
Fixed canonical matrices for CF14 semantic calculator.

These matrices are constants - they represent the fixed ontological structure
of the Chirality Framework. They are not dynamic or configurable.

This embodies the "semantic calculator" philosophy: we have specific,
unchanging inputs that produce predictable outputs through deterministic
semantic operations.
"""

from .types import Matrix, Cell


def _create_cell(row: int, col: int, value: str) -> Cell:
    """Helper to create a cell with minimal provenance."""
    return Cell(
        row=row,
        col=col,
        value=value,
        provenance={"source": "canonical_matrix"}
    )


def _create_matrix_cells(content: list[list[str]]) -> list[list[Cell]]:
    """Convert 2D string array to 2D Cell array."""
    return [
        [_create_cell(row, col, content[row][col]) for col in range(len(content[row]))]
        for row in range(len(content))
    ]


# Fixed canonical Matrix A (3x4)
MATRIX_A = Matrix(
    name="A",
    station="Problem Statement",
    row_labels=["Normative", "Operative", "Evaluative"],
    col_labels=["Guiding", "Applying", "Judging", "Reflecting"],
    cells=_create_matrix_cells([
        ["Values", "Actions", "Benchmarks", "Feedback"],
        ["Principles", "Methods", "Standards", "Adaptation"],
        ["Objectives", "Coordination", "Evaluation", "Consolidation"]
    ])
)

# Fixed canonical Matrix B (4x4)  
MATRIX_B = Matrix(
    name="B",
    station="Problem Statement",
    row_labels=["Data", "Information", "Knowledge", "Wisdom"],
    col_labels=["Determinacy", "Sufficiency", "Completeness", "Consistency"],
    cells=_create_matrix_cells([
        ["Necessary", "Sufficient", "Complete", "Probability"],
        ["Contingent", "Insufficient", "Incomplete", "Possibility"],
        ["Fundamental", "Appropriate", "Holistic", "Feasibility"],
        ["Best Practices", "Limits of", "Justification for", "Practicality"]
    ])
)

# Fixed canonical Matrix J (3x4) - Truncated B without "Wisdom" row
MATRIX_J = Matrix(
    name="J",
    station="Objectives",
    row_labels=["Data", "Information", "Knowledge"],  # No "Wisdom" row
    col_labels=["Determinacy", "Sufficiency", "Completeness", "Consistency"],
    cells=_create_matrix_cells([
        ["Necessary", "Sufficient", "Complete", "Probability"],
        ["Contingent", "Insufficient", "Incomplete", "Possibility"],
        ["Fundamental", "Appropriate", "Holistic", "Feasibility"]
    ])
)


def get_canonical_matrix(name: str) -> Matrix:
    """
    Get a canonical matrix by name.
    
    Args:
        name: Matrix name ("A", "B", or "J")
        
    Returns:
        The canonical matrix
        
    Raises:
        ValueError: If matrix name is not recognized
    """
    matrices = {"A": MATRIX_A, "B": MATRIX_B, "J": MATRIX_J}
    
    if name not in matrices:
        raise ValueError(f"Unknown canonical matrix: {name}. Available: A, B, J")
    
    return matrices[name]


def validate_canonical_matrices():
    """
    Validate that the canonical matrices have the expected structure.
    
    This is a sanity check to ensure the fixed matrices are properly defined.
    """
    # Validate Matrix A (3x4)
    assert MATRIX_A.shape == (3, 4), f"Matrix A should be 3x4, got {MATRIX_A.shape}"
    assert len(MATRIX_A.row_labels) == 3, f"Matrix A should have 3 row labels"
    assert len(MATRIX_A.col_labels) == 4, f"Matrix A should have 4 column labels"
    
    # Validate Matrix B (4x4)
    assert MATRIX_B.shape == (4, 4), f"Matrix B should be 4x4, got {MATRIX_B.shape}"
    assert len(MATRIX_B.row_labels) == 4, f"Matrix B should have 4 row labels"
    assert len(MATRIX_B.col_labels) == 4, f"Matrix B should have 4 column labels"
    
    # Validate Matrix J (3x4) - truncated B
    assert MATRIX_J.shape == (3, 4), f"Matrix J should be 3x4, got {MATRIX_J.shape}"
    assert len(MATRIX_J.row_labels) == 3, f"Matrix J should have 3 row labels"
    assert len(MATRIX_J.col_labels) == 4, f"Matrix J should have 4 column labels"
    
    # Ensure J is properly truncated B (first 3 rows)
    for i in range(3):
        for j in range(4):
            assert MATRIX_B.cells[i][j].value == MATRIX_J.cells[i][j].value, \
                f"Matrix J cell [{i}][{j}] should match Matrix B"


if __name__ == "__main__":
    # Run validation if script is executed directly
    validate_canonical_matrices()
    print("✓ All canonical matrices validated successfully")
    print(f"✓ Matrix A: {MATRIX_A.shape} - {MATRIX_A.station}")
    print(f"✓ Matrix B: {MATRIX_B.shape} - {MATRIX_B.station}")
    print(f"✓ Matrix J: {MATRIX_J.shape} - {MATRIX_J.station}")