"""
Simplified types for CF14 semantic calculator.

Contains only the essential data structures: Cell, Matrix, Operation.
All abstractions removed - this is a fixed algorithm, not a flexible framework.
"""

from typing import Any, Dict, List, Optional, Literal
from dataclasses import dataclass, field


@dataclass
class Cell:
    """
    Fundamental semantic unit in CF14 semantic calculator.
    
    Stores the result of the 3-stage interpretation pipeline:
    - Stage 1 (Combinatorial): k-products generated mechanically
    - Stage 2 (Semantic): Word pairs resolved to concepts
    - Stage 3 (Lensing): Ontological interpretation applied
    
    Attributes:
        row: Row position in matrix
        col: Column position in matrix  
        value: Final semantic result after 3-stage pipeline
        provenance: Dict storing all intermediate results from each stage
    """
    row: int
    col: int
    value: str
    provenance: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Matrix:
    """
    2D semantic matrix for CF14 semantic calculator.
    
    Contains cells arranged in a fixed ontological structure where:
    - row_labels define the row ontological axis
    - col_labels define the column ontological axis  
    - Each cell represents the semantic intersection of its row/column coordinates
    
    Attributes:
        name: Matrix identifier (A, B, C, D, F, J)
        station: Valley station where matrix exists
        row_labels: Ontological labels for rows (e.g. ["Normative", "Operative", "Evaluative"]) 
        col_labels: Ontological labels for columns (e.g. ["Determinacy", "Sufficiency", etc.])
        cells: 2D array of cells [row][col]
    """
    name: str
    station: str
    row_labels: List[str]
    col_labels: List[str] 
    cells: List[List[Cell]]
    
    @property
    def shape(self) -> tuple[int, int]:
        """Get matrix dimensions."""
        return (len(self.row_labels), len(self.col_labels))
    
    def get_cell(self, row: int, col: int) -> Optional[Cell]:
        """Get cell at specific position."""
        if 0 <= row < len(self.cells) and 0 <= col < len(self.cells[row]):
            return self.cells[row][col]
        return None


@dataclass
class Operation:
    """
    Minimal operation record for CF14 semantic calculator.
    
    Simple logging-only record of semantic operations.
    No complex abstractions - just tracks what happened.
    """
    kind: Literal["*", "+", "interpret", "⊙", "synthesize"]
    inputs: List[str]          # Input matrix names
    output: str                # Output matrix name
    timestamp: str