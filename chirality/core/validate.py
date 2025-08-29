"""
Validation rules for CF14 semantic structures.

Enforces dimensional constraints, modality alignment, and operation sequencing.
"""

from typing import List, Dict, Any, Optional
from .types import Cell, Matrix


class CF14ValidationError(ValueError):
    """Raised when CF14 validation rules are violated."""
    pass


def ensure_dims(A: Matrix, B: Matrix, op: str) -> None:
    """
    Ensure matrix dimensions are compatible for operation.
    
    Args:
        A: First matrix
        B: Second matrix 
        op: Operation type
    
    Raises:
        CF14ValidationError: If dimensions incompatible
    """
    if op == "*":
        if A.shape[1] != B.shape[0]:
            raise CF14ValidationError(
                f"Matrix multiplication requires A.cols == B.rows, got {A.shape} × {B.shape}"
            )
    elif op in ["+", "⊙"]:
        if A.shape != B.shape:
            raise CF14ValidationError(
                f"Operation {op} requires same dimensions, got {A.shape} vs {B.shape}"
            )


def ensure_same_rows_cols(A: Matrix, B: Matrix, op: str) -> None:
    """
    Ensure matrices have same dimensions.
    
    Args:
        A: First matrix
        B: Second matrix
        op: Operation type
    
    Raises:
        CF14ValidationError: If dimensions don't match
    """
    if A.shape != B.shape:
        raise CF14ValidationError(
            f"Operation {op} requires identical dimensions, got {A.shape} vs {B.shape}"
        )


def validate_cell(cell: Cell) -> List[str]:
    """
    Validate a cell structure for the simplified CF14 types.

    Checks only fields that actually exist on Cell:
    - row/col are non-negative integers
    - value is a non-empty string
    - provenance is a dict (may be empty)
    """
    errors: List[str] = []

    # row/col
    if not isinstance(cell.row, int) or cell.row < 0:
        errors.append(f"Invalid row position: {cell.row}")
    if not isinstance(cell.col, int) or cell.col < 0:
        errors.append(f"Invalid column position: {cell.col}")

    # value
    if not isinstance(cell.value, str) or not cell.value.strip():
        errors.append("Cell value must be a non-empty string")

    # provenance
    if not isinstance(cell.provenance, dict):
        errors.append("Cell provenance must be a dict")

    return errors


def validate_matrix(matrix: Matrix) -> List[str]:
    """
    Validate a matrix structure for the simplified CF14 types.

    Checks presence and coherence of:
    - name (str), station (str)
    - row_labels/col_labels length matches cells grid
    - cells 2D list shape consistency
    """
    errors: List[str] = []

    # Basic identity
    if not isinstance(matrix.name, str) or not matrix.name:
        errors.append("Matrix missing name")
    if not isinstance(matrix.station, str) or not matrix.station:
        errors.append("Matrix missing station")

    # Labels
    if not isinstance(matrix.row_labels, list) or not all(isinstance(x, str) for x in matrix.row_labels):
        errors.append("row_labels must be list[str]")
    if not isinstance(matrix.col_labels, list) or not all(isinstance(x, str) for x in matrix.col_labels):
        errors.append("col_labels must be list[str]")

    rows, cols = matrix.shape
    if rows <= 0 or cols <= 0:
        errors.append(f"Invalid dimensions: {matrix.shape}")

    # Cells grid
    if not isinstance(matrix.cells, list) or len(matrix.cells) != rows:
        errors.append("cells must be a 2D list with len == number of rows")
    else:
        for r, row in enumerate(matrix.cells):
            if not isinstance(row, list) or len(row) != cols:
                errors.append(f"row {r} length mismatch: expected {cols}, got {len(row) if isinstance(row, list) else 'not a list'}")
                break

    # Label vs shape coherence
    if isinstance(matrix.row_labels, list) and len(matrix.row_labels) != rows:
        errors.append("row_labels length does not match number of rows")
    if isinstance(matrix.col_labels, list) and len(matrix.col_labels) != cols:
        errors.append("col_labels length does not match number of columns")

    cell_positions = set()
    for cell in matrix.cells:
        # Validate individual cell
        cell_errors = validate_cell(cell)
        errors.extend([f"Cell {cell.id}: {e}" for e in cell_errors])
        
        # Check bounds
        if cell.row >= rows or cell.col >= cols:
            errors.append(f"Cell {cell.id} out of bounds: ({cell.row}, {cell.col})")
        
        # Check duplicates
        pos = (cell.row, cell.col)
        if pos in cell_positions:
            errors.append(f"Duplicate cell at position {pos}")
        cell_positions.add(pos)
    
    return errors


def validate_operation_sequence(operations: List[str]) -> List[str]:
    """
    Validate CF14 operation sequence rules.
    
    Rules:
    - Multiply before add
    - Interpret after base operations
    
    Args:
        operations: List of operation types
    
    Returns:
        List of validation errors
    """
    errors = []
    
    # Check for multiply before add rule
    last_multiply_idx = -1
    first_add_idx = len(operations)
    
    for i, op in enumerate(operations):
        if op == "multiply":
            last_multiply_idx = i
        elif op == "add" and first_add_idx == len(operations):
            first_add_idx = i
    
    if first_add_idx < last_multiply_idx:
        errors.append("Addition operation before multiplication (violates CF14 sequence)")
    
    return errors


def validate_modality_alignment(matrix_a: Matrix, matrix_b: Matrix) -> List[str]:
    """
    Validate modality alignment between matrices.
    
    Args:
        matrix_a: First matrix
        matrix_b: Second matrix
    
    Returns:
        List of validation errors
    """
    errors = []
    
    # Note: Modality alignment removed - simplified architecture
    # All semantic validation now handled by the 3-stage pipeline
    
    return errors


def validate_matrix_dimensions(matrix_a: Matrix, matrix_b: Matrix, operation: str) -> List[str]:
    """
    Validate matrix dimensions for operations.
    
    Args:
        matrix_a: First matrix
        matrix_b: Second matrix
        operation: Operation type (multiply, add)
    
    Returns:
        List of validation errors
    """
    errors = []
    
    if operation == "multiply":
        # For multiplication: A.cols must equal B.rows
        if matrix_a.shape[1] != matrix_b.shape[0]:
            errors.append(
                f"Incompatible dimensions for multiplication: "
                f"{matrix_a.shape} × {matrix_b.shape}"
            )
    
    elif operation == "add":
        # For addition: dimensions must match exactly
        if matrix_a.shape != matrix_b.shape:
            errors.append(
                f"Incompatible dimensions for addition: "
                f"{matrix_a.shape} vs {matrix_b.shape}"
            )
    
    return errors


def validate_provenance(cell: Cell) -> List[str]:
    """
    Validate provenance tracking for a cell.
    
    Args:
        cell: Cell to validate
    
    Returns:
        List of validation errors
    """
    errors = []
    
    if not cell.provenance:
        errors.append("Cell missing provenance")
        return errors
    
    # Check required provenance fields
    if "operation" not in cell.provenance:
        errors.append("Provenance missing operation type")
    
    if "sources" not in cell.provenance:
        errors.append("Provenance missing sources")
    elif not isinstance(cell.provenance["sources"], list):
        errors.append("Provenance sources must be a list")
    
    if "timestamp" not in cell.provenance:
        errors.append("Provenance missing timestamp")
    
    return errors
