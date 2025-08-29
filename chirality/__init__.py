"""
Chirality Framework - CF14 Semantic Calculator.

A fixed, canonical "semantic calculator" for structured problem-solving.
Not a framework but a precise algorithm with a 3-stage interpretation pipeline.
"""

__version__ = "15.0.0"
__author__ = "Chirality Framework Team"

from .core.types import Cell, Matrix, Operation
from .core.context import SemanticContext
from .core.cell_resolver import CellResolver
from .core.resolvers import EchoResolver
from .core.operations import (
    compute_cell_C,
    compute_cell_F,
    synthesize_cell_D,
    compute_matrix_C,
    compute_matrix_F,
    synthesize_matrix_D
)
from .core.matrices import MATRIX_A, MATRIX_B, MATRIX_J
from .core.validate import CF14ValidationError, validate_matrix, validate_cell
from .core.tracer import JSONLTracer

__all__ = [
    # Core types
    "Cell",
    "Matrix", 
    "Operation",
    "SemanticContext",
    # Canonical matrices
    "MATRIX_A",
    "MATRIX_B",
    "MATRIX_J",
    # Resolvers
    "CellResolver",
    "EchoResolver",
    # Cell-level operations (the core algorithm)
    "compute_cell_C",
    "compute_cell_F",
    "synthesize_cell_D",
    # Matrix-level operations (convenience wrappers)
    "compute_matrix_C",
    "compute_matrix_F",
    "synthesize_matrix_D",
    # Validation
    "CF14ValidationError",
    "validate_matrix",
    "validate_cell",
    # Tracing
    "JSONLTracer",
]