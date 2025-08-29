"""
Core CF14 semantic calculator modules.
"""

from .types import Cell, Matrix, Operation
from .context import SemanticContext
from .cell_resolver import CellResolver
from .resolvers import EchoResolver
from .operations import (
    compute_cell_C,
    compute_cell_F,
    synthesize_cell_D,
    compute_matrix_C,
    compute_matrix_F,
    synthesize_matrix_D
)
from .matrices import MATRIX_A, MATRIX_B, MATRIX_J
from .validate import CF14ValidationError
from .tracer import JSONLTracer

__all__ = [
    # Core types
    "Cell", "Matrix", "Operation", "SemanticContext",
    # Resolvers
    "CellResolver", "EchoResolver",
    # Operations (cell-level)
    "compute_cell_C", "compute_cell_F", "synthesize_cell_D",
    # Operations (matrix-level)
    "compute_matrix_C", "compute_matrix_F", "synthesize_matrix_D",
    # Canonical matrices
    "MATRIX_A", "MATRIX_B", "MATRIX_J",
    # Validation
    "CF14ValidationError",
    # Tracing
    "JSONLTracer",
]