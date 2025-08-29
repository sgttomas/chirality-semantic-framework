# API Reference - Chirality Framework v15.0.0

**Comprehensive reference for the CF14 Semantic Calculator API**

## Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Core Types](#core-types)
3. [Canonical Matrices](#canonical-matrices)
4. [Cell-Level Operations](#cell-level-operations)
5. [Matrix-Level Operations](#matrix-level-operations)
6. [Resolvers](#resolvers)
7. [Context & Tracing](#context--tracing)
8. [Working Memory Export](#working-memory-export)
9. [Validation](#validation)
10. [CLI Reference](#cli-reference)
11. [Error Handling](#error-handling)
12. [Examples](#examples)

---

## Installation & Setup

### Basic Installation
```bash
pip install chirality-framework==15.0.0
```

### With Optional Dependencies
```bash
pip install chirality-framework[all]==15.0.0    # OpenAI + Neo4j
pip install chirality-framework[openai]==15.0.0 # Just OpenAI
pip install chirality-framework[neo4j]==15.0.0  # Just Neo4j
```

### Environment Variables
```bash
export OPENAI_API_KEY="sk-your-key-here"     # Required for OpenAI resolver
export NEO4J_URI="bolt://localhost:7687"     # Optional for Neo4j export  
export NEO4J_USER="neo4j"                    # Optional for Neo4j export
export NEO4J_PASSWORD="password"             # Optional for Neo4j export
```

---

## Core Types

### Cell

Fundamental semantic unit storing the result of the 3-stage interpretation pipeline.

```python
from chirality import Cell

@dataclass
class Cell:
    row: int                        # Row position in matrix
    col: int                        # Column position in matrix  
    value: str                      # Final semantic result
    provenance: Dict[str, Any]      # Complete stage history
```

**Key Provenance Fields:**
- `stage_1_products`: Mechanical k-products from combinatorial stage
- `stage_2_resolved`: Semantic concepts from resolution stage  
- `stage_3_lensed`: Final interpretation from lensing stage
- `operation`: Operation type ("compute_C", "compute_F", "synthesize_D")
- `coordinates`: Human-readable coordinate description
- `traced`: Boolean indicating if tracing was enabled

**Example:**
```python
cell = compute_cell_C(0, 0, A, B, resolver, valley_summary)
print(f"Result: {cell.value}")
print(f"Products: {cell.provenance['stage_1_products']}")
print(f"Resolved: {cell.provenance['stage_2_resolved']}")
```

### Matrix

2D semantic matrix with fixed ontological structure.

```python
from chirality import Matrix

@dataclass  
class Matrix:
    name: str                       # Matrix identifier (A, B, C, D, F, J)
    station: str                    # Valley station context
    row_labels: List[str]           # Ontological row axis labels
    col_labels: List[str]           # Ontological column axis labels  
    cells: List[List[Cell]]         # 2D array of cells [row][col]
    
    @property
    def shape(self) -> tuple[int, int]:
        """Get matrix dimensions (rows, cols)."""
        
    def get_cell(self, row: int, col: int) -> Optional[Cell]:
        """Get cell at specific position."""
```

**Example:**
```python
from chirality import MATRIX_A
print(f"Matrix A shape: {MATRIX_A.shape}")  # (3, 4)
print(f"Row labels: {MATRIX_A.row_labels}")  # ["Normative", "Operative", "Evaluative"]
cell = MATRIX_A.get_cell(0, 0)
print(f"A[0,0] = {cell.value}")  # "Values"
```

### SemanticContext

Complete context for semantic operations in the three-stage pipeline.

```python
from chirality import SemanticContext

@dataclass
class SemanticContext:
    # Valley position
    station_context: str            # "Requirements", "Objectives", etc.
    valley_summary: str             # Full valley navigation context
    
    # Ontological coordinates  
    row_label: str                  # Row ontology ("Normative", etc.)
    col_label: str                  # Column ontology ("Necessity", etc.)
    
    # Operation specifics
    operation_type: str             # "*", "⊙", "synthesize", "interpret"
    terms: Dict[str, Any]           # Actual content to process
    
    # Optional tracing coordinates
    matrix: Optional[str] = None    # "C", "F", "D" 
    i: Optional[int] = None         # Row index
    j: Optional[int] = None         # Column index
    
    # Optional customization
    operation_instructions: Optional[str] = None
    system_frame: Optional[str] = None
```

---

## Canonical Matrices

Fixed ontological matrices that form the foundation of all computations.

### MATRIX_A (Axioms - 3×4)
```python
from chirality import MATRIX_A

# Station: Problem Statement
# Row labels: ["Normative", "Operative", "Evaluative"] 
# Col labels: ["Guiding", "Applying", "Judging", "Reviewing"]
# Content: Values, Actions, Standards, Methods, etc.
```

### MATRIX_B (Bridge - 4×4)  
```python
from chirality import MATRIX_B

# Station: Problem Statement
# Row labels: ["Data", "Information", "Knowledge", "Wisdom"]
# Col labels: ["Necessity (vs Contingency)", "Sufficiency", "Completeness", "Consistency"]
# Content: Necessary vs Contingent, Sufficient, Complete, etc.
```

### MATRIX_J (Judgment - 3×4)
```python
from chirality import MATRIX_J

# Station: Verification
# Row labels: ["Data", "Information", "Knowledge"]  # Truncated from B (no "Wisdom" row)
# Col labels: ["Necessity (vs Contingency)", "Sufficiency", "Completeness", "Consistency"]
# Content: Mirrors the first three rows of B (e.g., Necessary, Contingent, Fundamental, ...)
```

**Matrix Relationships:**
- **C = A * B**: Requirements matrix from axiom-bridge multiplication
- **F = J ⊙ C**: Functions matrix from element-wise judgment-requirements
- **D = synthesis(A, F)**: Solution objectives from axiom-function synthesis

---

## Cell-Level Operations

The core algorithm - these functions implement the three-stage interpretation pipeline.

### compute_cell_C()

Matrix multiplication cell: C[i,j] = A[i,:] dot B[:,j]

```python
from chirality import compute_cell_C, MATRIX_A, MATRIX_B, CellResolver

def compute_cell_C(
    i: int,                                    # Row index (0-2)
    j: int,                                    # Column index (0-3)  
    A: Matrix,                                 # Left matrix (3×4)
    B: Matrix,                                 # Right matrix (4×4)
    resolver: CellResolver,                    # LLM interface
    valley_summary: str,                       # Valley context
    tracer: Optional[JSONLTracer] = None,      # Optional tracing
    exporter: Optional[Neo4jWorkingMemoryExporter] = None  # Optional Neo4j export
) -> Cell
```

**Three-Stage Pipeline:**
1. **Stage 1**: Generate k-products: `A[i,k] * B[k,j]` for k=0,1,2,3
2. **Stage 2**: Resolve each pair semantically via LLM  
3. **Stage 3**: Apply ontological lens through row/column coordinates

**Example:**
```python
resolver = CellResolver(api_key="sk-...")
valley = "Problem Statement → [Requirements] → Objectives"

cell = compute_cell_C(0, 0, MATRIX_A, MATRIX_B, resolver, valley)
print(f"C[0,0]: {cell.value}")
print(f"Products: {cell.provenance['stage_1_products']}")
```

### compute_cell_F()

Element-wise multiplication cell: F[i,j] = J[i,j] ⊙ C[i,j]

```python
def compute_cell_F(
    i: int,                                    # Row index (0-2)
    j: int,                                    # Column index (0-3)
    J: Matrix,                                 # Judgment matrix (3×4)
    C: Matrix,                                 # Composition matrix (3×4) 
    resolver: CellResolver,                    # LLM interface
    valley_summary: str,                       # Valley context
    tracer: Optional[JSONLTracer] = None,      # Optional tracing
    exporter: Optional[Neo4jWorkingMemoryExporter] = None  # Optional export
) -> Cell
```

**Two-Stage Pipeline:**
1. **Stage 1**: Direct element-wise multiplication (same coordinates)
2. **Stage 2**: Apply ontological lens for Objectives station context

**Example:**
```python
# First compute C matrix
C = compute_matrix_C(MATRIX_A, MATRIX_B, resolver, valley)

# Then compute F cell
cell = compute_cell_F(0, 0, MATRIX_J, C, resolver, valley)
print(f"F[0,0]: {cell.value}")
```

### synthesize_cell_D()

Synthesis operation using canonical D formula.

```python
def synthesize_cell_D(
    i: int,                                    # Row index (0-2)
    j: int,                                    # Column index (0-3)
    A: Matrix,                                 # Axioms matrix (3×4)
    F: Matrix,                                 # Functions matrix (3×4)
    problem: str,                              # Problem statement
    resolver: CellResolver,                    # LLM interface  
    valley_summary: str,                       # Valley context
    tracer: Optional[JSONLTracer] = None,      # Optional tracing
    exporter: Optional[Neo4jWorkingMemoryExporter] = None  # Optional export
) -> Cell
```

**Formula**: `D[i,j] = A[i,j] + "applied to frame the problem of {problem} and" + F[i,j] + "to resolve the problem"`

**Two-Stage Pipeline:**
1. **Stage 1**: Apply synthesis formula mechanically  
2. **Stage 2**: Apply ontological lens for Solution Objectives context

**Example:**
```python
# Compute prerequisite matrices
C = compute_matrix_C(MATRIX_A, MATRIX_B, resolver, valley)
F = compute_matrix_F(MATRIX_J, C, resolver, valley)

# Synthesize D cell
cell = synthesize_cell_D(0, 0, MATRIX_A, F, "creating value", resolver, valley)
print(f"D[0,0]: {cell.value}")
```

---

## Matrix-Level Operations

Convenience wrappers that compute entire matrices by iterating over cell functions.

### compute_matrix_C()

```python
def compute_matrix_C(
    A: Matrix,                                 # Left matrix (3×4) 
    B: Matrix,                                 # Right matrix (4×4)
    resolver: CellResolver,                    # LLM interface
    valley_summary: str,                       # Valley context
    tracer: Optional[JSONLTracer] = None,      # Optional tracing
    exporter: Optional[Neo4jWorkingMemoryExporter] = None  # Optional export
) -> Matrix                                    # Result matrix (3×4)
```

**Usage:**
```python
C = compute_matrix_C(MATRIX_A, MATRIX_B, resolver, valley)
print(f"Generated {C.shape[0]}×{C.shape[1]} requirements matrix")
```

### compute_matrix_F()

```python
def compute_matrix_F(
    J: Matrix,                                 # Judgment matrix (3×4)
    C: Matrix,                                 # Composition matrix (3×4)
    resolver: CellResolver,                    # LLM interface
    valley_summary: str,                       # Valley context  
    tracer: Optional[JSONLTracer] = None,      # Optional tracing
    exporter: Optional[Neo4jWorkingMemoryExporter] = None  # Optional export
) -> Matrix                                    # Result matrix (3×4)
```

### synthesize_matrix_D()

```python
def synthesize_matrix_D(
    A: Matrix,                                 # Axioms matrix (3×4)
    F: Matrix,                                 # Functions matrix (3×4) 
    problem: str,                              # Problem statement
    resolver: CellResolver,                    # LLM interface
    valley_summary: str,                       # Valley context
    tracer: Optional[JSONLTracer] = None,      # Optional tracing
    exporter: Optional[Neo4jWorkingMemoryExporter] = None  # Optional export  
) -> Matrix                                    # Result matrix (3×4)
```

---

## Resolvers

### CellResolver

Primary LLM interface for semantic operations.

```python
from chirality import CellResolver

class CellResolver:
    def __init__(
        self, 
        api_key: Optional[str] = None,         # OpenAI API key (or env var)
        model: str = "gpt-4o",                 # OpenAI model to use
        seed: int = 42                         # Seed for reproducibility
    ):
```

**Key Methods:**
```python
def resolve_semantic_pair(self, pair: str, context: SemanticContext) -> str:
    """Stage 2: Resolve word pair into coherent concept."""
    
def apply_ontological_lens(self, content: str, context: SemanticContext) -> str:
    """Stage 3: Apply row/column ontological interpretation."""
    
def assemble_prompt(self, valley_summary: str, station: str, row_label: str, 
                   col_label: str, operation_type: str, terms: Dict, 
                   operation_instructions: str = None) -> str:
    """Fragment composition - dynamically build prompts."""
```

**Temperature Settings:**
```python
resolver.temperatures = {
    "multiply": 0.7,  # Creative for semantic multiplication
    "add": 0.5,       # Structured for semantic addition  
    "interpret": 0.5, # Clear for interpretation
    "*": 0.7,         # Alias for multiply
    "+": 0.5,         # Alias for add
    "⊙": 0.7          # Element-wise multiplication
}
```

### EchoResolver  

Deterministic test resolver (no LLM calls).

```python
from chirality import EchoResolver

class EchoResolver:
    def resolve(self, op: str, inputs: List[Matrix], system_prompt: str, 
               user_prompt: str, context: Dict[str, Any]) -> List[List[str]]:
        """Return predictable outputs based on operation type."""
```

**Usage:**
```python
# Perfect for testing pipeline mechanics without LLM costs
echo_resolver = EchoResolver()
cell = compute_cell_C(0, 0, MATRIX_A, MATRIX_B, echo_resolver, valley)
```

---

## Context & Tracing

### SemanticContext

Complete context object for semantic operations.

```python
from chirality import SemanticContext

# Create context for Stage 2 resolution
context = SemanticContext(
    station_context="Requirements",
    valley_summary="Problem Statement → [Requirements] → Objectives",
    row_label="Normative",
    col_label="Necessity (vs Contingency)",
    operation_type="*",
    terms={"pair": "Values * Necessary vs Contingent"},
    matrix="C",      # Optional for tracing
    i=0,             # Optional for tracing
    j=0              # Optional for tracing
)
```

### JSONLTracer

Production-ready tracing system for semantic journey tracking.

```python
from chirality import JSONLTracer

class JSONLTracer:
    def __init__(
        self,
        base_path: Path = Path("traces"),      # Trace file directory
        thread_id: str = None,                 # Session identifier
        dedupe: bool = True,                   # Content deduplication  
        max_bytes: int = 50 * 1024 * 1024,     # File rotation size
        max_seen: int = 100_000                # Deduplication cache size
    ):
```

**Key Methods:**
```python
def trace_stage(self, stage: str, context: SemanticContext, 
               result: Dict, extras: Dict) -> None:
    """Record a single stage execution."""
    
def close(self) -> None:
    """Flush and close trace file."""
```

**Usage:**
```python
# Enable tracing for complete observability
with JSONLTracer(thread_id="debug-session") as tracer:
    cell = compute_cell_C(0, 0, A, B, resolver, valley, tracer)
    
# Trace files written to traces/debug-session/
```

---

## Working Memory Export

### Neo4jWorkingMemoryExporter

Exports complete semantic journey to Neo4j graph database.

```python
from chirality.exporters.working_memory_exporter import Neo4jWorkingMemoryExporter

class Neo4jWorkingMemoryExporter:
    def __init__(
        self,
        uri: str = None,                       # Neo4j URI (or env var)
        user: str = None,                      # Username (or env var) 
        password: str = None                   # Password (or env var)
    ):
```

**Methods:**
```python
def export_cell_computation(self, cell: Cell, context: SemanticContext) -> None:
    """Export complete cell journey to graph."""
    
def close(self) -> None:
    """Close database connection."""
```

**Graph Schema:**
- **(:Matrix)** nodes: Represent matrices (A, B, C, D, F, J)
- **(:Cell)** nodes: Individual cells with coordinates and values
- **(:Stage)** nodes: Pipeline stages (Combinatorial, Semantic, Lensed)
- **[:CONTAINS]** relationships: Matrix → Cell
- **[:HAS_STAGE]** relationships: Cell → Stage

**Usage:**
```python
# Export semantic journey to working memory
with Neo4jWorkingMemoryExporter() as exporter:
    cell = compute_cell_C(0, 0, A, B, resolver, valley, exporter=exporter)
    
# Query the working memory
# MATCH (c:Cell {id: 'C-0-0'})-[:HAS_STAGE]->(s) RETURN s ORDER BY s.timestamp
```

---

## Validation

### Validation Functions

```python
from chirality import validate_matrix, validate_cell, CF14ValidationError

def validate_matrix(matrix: Matrix) -> List[str]:
    """Validate matrix structure and return list of errors."""
    
def validate_cell(cell: Cell) -> List[str]:
    """Validate cell structure and return list of errors."""
    
class CF14ValidationError(ValueError):
    """Raised when CF14 validation rules are violated."""
```

**Example:**
```python
errors = validate_matrix(MATRIX_A)
if errors:
    print("Validation errors:", errors)
else:
    print("Matrix is valid")
```

---

## CLI Reference

### Main Commands

#### compute-cell
Compute a single cell through the 3-stage pipeline.

```bash
python3 -m chirality.cli compute-cell MATRIX --i ROW --j COL [OPTIONS]
```

**Arguments:**
- `MATRIX`: Matrix type (C, F, D)
- `--i ROW`: Row index (0-2) 
- `--j COL`: Column index (0-3)

**Options:**
- `--verbose, -v`: Show intermediate results from each stage
- `--resolver [echo|openai]`: Resolver to use (default: echo)
- `--api-key`: OpenAI API key (or set OPENAI_API_KEY env var)
- `--trace/--no-trace`: Enable JSONL tracing (default: false)
- `--neo4j-export/--no-neo4j-export`: Export to Neo4j (default: false)
- `--problem TEXT`: Problem statement for D matrix synthesis

**Examples:**
```bash
# Basic computation with echo resolver
python3 -m chirality.cli compute-cell C --i 0 --j 0

# Verbose output showing all 3 stages  
python3 -m chirality.cli compute-cell C --i 0 --j 0 --verbose

# Use OpenAI resolver with API key
python3 -m chirality.cli compute-cell C --i 0 --j 0 --resolver openai --verbose

# Full observability - tracing + Neo4j export
python3 -m chirality.cli compute-cell C --i 0 --j 0 --trace --neo4j-export

# Compute different matrix types
python3 -m chirality.cli compute-cell F --i 1 --j 2 --verbose  
python3 -m chirality.cli compute-cell D --i 2 --j 1 --problem "creating value"
```

#### info
Display information about the semantic calculator.

```bash
python3 -m chirality.cli info
```

Shows:
- Version information
- Canonical matrices overview  
- Result matrices explanation
- 3-stage pipeline summary

---

## Error Handling

### Common Exceptions

```python
# Import errors
from chirality import CF14ValidationError

try:
    cell = compute_cell_C(0, 0, A, B, resolver, valley)
except CF14ValidationError as e:
    print(f"Validation error: {e}")
except ValueError as e:
    print(f"Configuration error: {e}")  
except ImportError as e:
    print(f"Dependency missing: {e}")
```

### API Key Errors
```python
# CellResolver requires valid API key
try:
    resolver = CellResolver(api_key="invalid-key")
except ValueError as e:
    print("OpenAI API key required")
```

### Neo4j Connection Errors  
```python
# Neo4j exporter handles connection failures gracefully
try:
    exporter = Neo4jWorkingMemoryExporter(uri="bolt://invalid:7687")
except Exception as e:
    print(f"Neo4j connection failed: {e}")
```

---

## Examples

### Basic Usage

```python
from chirality import (
    MATRIX_A, MATRIX_B, MATRIX_J,
    CellResolver, EchoResolver,
    compute_cell_C, compute_matrix_C,
    JSONLTracer
)

# Test with echo resolver (fast, deterministic)
echo_resolver = EchoResolver()
valley = "Problem Statement → [Requirements] → Objectives → Solution"

cell = compute_cell_C(0, 0, MATRIX_A, MATRIX_B, echo_resolver, valley)
print(f"Echo result: {cell.value}")

# Full matrix computation  
C = compute_matrix_C(MATRIX_A, MATRIX_B, echo_resolver, valley)
print(f"Requirements matrix: {C.shape}")
```

### Production Usage

```python
import os
from chirality import (
    CellResolver, JSONLTracer, 
    compute_cell_C, compute_matrix_F, synthesize_matrix_D,
    MATRIX_A, MATRIX_B, MATRIX_J
)
from chirality.exporters.working_memory_exporter import Neo4jWorkingMemoryExporter

# Setup production resolver
resolver = CellResolver(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o",
    seed=42
)

valley = "Problem Statement → [Requirements] → Objectives → Solution Objectives"

# Full pipeline with tracing and Neo4j export
with JSONLTracer(thread_id="production-run") as tracer:
    with Neo4jWorkingMemoryExporter() as exporter:
        
        # Generate requirements matrix
        C = compute_matrix_C(MATRIX_A, MATRIX_B, resolver, valley, tracer, exporter)
        
        # Generate functions matrix  
        F = compute_matrix_F(MATRIX_J, C, resolver, valley, tracer, exporter)
        
        # Generate solution objectives
        D = synthesize_matrix_D(MATRIX_A, F, "optimizing performance", 
                               resolver, valley, tracer, exporter)

print("Complete semantic valley computed with full observability")
```

### Debugging Workflow

```python
from chirality import compute_cell_C, MATRIX_A, MATRIX_B, EchoResolver

# Step 1: Test with echo resolver to verify pipeline mechanics
echo_resolver = EchoResolver()
echo_cell = compute_cell_C(0, 0, MATRIX_A, MATRIX_B, echo_resolver, valley)
print("Echo test passed - pipeline mechanics work")

# Step 2: Test with OpenAI resolver  
openai_resolver = CellResolver(api_key="sk-...")
openai_cell = compute_cell_C(0, 0, MATRIX_A, MATRIX_B, openai_resolver, valley)
print("OpenAI test passed - semantic resolution works")

# Step 3: Compare results
print(f"Echo: {echo_cell.value}")
print(f"OpenAI: {openai_cell.value}")
```

### Custom Context Example

```python
from chirality import SemanticContext, CellResolver

# Create custom semantic context
context = SemanticContext(
    station_context="Custom Requirements",
    valley_summary="Custom Valley: Problem → [Custom] → Solution", 
    row_label="Performance",
    col_label="Reliability",
    operation_type="*",
    terms={"pair": "Speed * Accuracy"},
    operation_instructions="Focus on practical trade-offs"
)

resolver = CellResolver()
result = resolver.resolve_semantic_pair("Speed * Accuracy", context)
print(f"Custom resolution: {result}")
```

---

## Advanced Usage

### Prompt Engineering Integration

```python
# Test prompt modifications
from chirality.core.cell_resolver import CellResolver

class CustomCellResolver(CellResolver):
    def assemble_prompt(self, valley_summary, station, row_label, col_label,
                       operation_type, terms, operation_instructions=None):
        # Custom prompt assembly logic
        custom_prompt = f"""
        Enhanced Context: {valley_summary}
        Focus Area: {station}
        Ontological Intersection: {row_label} × {col_label}
        
        Operation: {operation_type}
        Terms: {terms}
        
        Custom Instructions: {operation_instructions or 'Standard processing'}
        """
        return custom_prompt

# Test custom prompts
custom_resolver = CustomCellResolver()
cell = compute_cell_C(0, 0, A, B, custom_resolver, valley)
```

### Batch Processing

```python
# Process multiple cells systematically  
cells_to_compute = [(0, 0), (0, 1), (1, 0), (1, 1)]
results = {}

for row, col in cells_to_compute:
    cell = compute_cell_C(row, col, MATRIX_A, MATRIX_B, resolver, valley)
    results[(row, col)] = cell.value
    
print("Batch results:", results)
```

### Performance Monitoring

```python
import time
from chirality import JSONLTracer

# Monitor performance with tracing
start_time = time.time()

with JSONLTracer(thread_id="performance-test") as tracer:
    cell = compute_cell_C(0, 0, A, B, resolver, valley, tracer)
    
elapsed = time.time() - start_time
print(f"Computation took {elapsed:.2f} seconds")

# Analyze trace file for latency breakdown
# traces/performance-test/C-YYYYMMDD-HHMMSS.jsonl
```

---

## Thread Safety & Concurrency

### Safe Concurrent Usage

```python
import concurrent.futures
from chirality import CellResolver, MATRIX_A, MATRIX_B

# CellResolver is thread-safe for concurrent cell computations
def compute_cell_worker(coords):
    row, col = coords
    resolver = CellResolver()  # Each thread gets its own resolver
    return compute_cell_C(row, col, MATRIX_A, MATRIX_B, resolver, valley)

# Compute multiple cells concurrently
coords = [(0, 0), (0, 1), (0, 2), (0, 3)]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    cells = list(executor.map(compute_cell_worker, coords))

print(f"Computed {len(cells)} cells concurrently")
```

### Tracing in Concurrent Context

```python
# Each thread should use separate tracer instances
def compute_with_tracing(coords, thread_id):
    row, col = coords
    tracer = JSONLTracer(thread_id=f"worker-{thread_id}")
    resolver = CellResolver()
    
    try:
        return compute_cell_C(row, col, A, B, resolver, valley, tracer)
    finally:
        tracer.close()
```

---

## Integration Patterns

### Flask/FastAPI Integration

```python
from flask import Flask, request, jsonify
from chirality import compute_cell_C, CellResolver, MATRIX_A, MATRIX_B

app = Flask(__name__)
resolver = CellResolver()

@app.route('/api/compute-cell', methods=['POST'])
def api_compute_cell():
    data = request.json
    row, col = data['row'], data['col'] 
    valley = data.get('valley', 'Default valley context')
    
    try:
        cell = compute_cell_C(row, col, MATRIX_A, MATRIX_B, resolver, valley)
        return jsonify({
            'value': cell.value,
            'provenance': cell.provenance,
            'coordinates': (row, col)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400
```

### Jupyter Notebook Usage

```python
# Perfect for interactive semantic exploration
from chirality import *

# Setup
resolver = CellResolver()
valley = "Problem Statement → [Requirements] → Objectives"

# Interactive cell computation
def explore_cell(row, col):
    cell = compute_cell_C(row, col, MATRIX_A, MATRIX_B, resolver, valley)
    
    print(f"=== C[{row},{col}] ===")
    print(f"Coordinates: ({MATRIX_A.row_labels[row]}, {MATRIX_B.col_labels[col]})")
    print(f"Result: {cell.value}")
    print(f"\nStage 1 Products:")
    for i, product in enumerate(cell.provenance['stage_1_products']):
        print(f"  k={i}: {product}")
    print(f"\nStage 2 Resolved:")  
    for i, concept in enumerate(cell.provenance['stage_2_resolved']):
        print(f"  {i}: {concept}")
    print(f"\nStage 3 Lensed:")
    print(f"  {cell.provenance['stage_3_lensed']}")

# Explore interactively
explore_cell(0, 0)  # Normative × Necessity
explore_cell(1, 2)  # Operative × Completeness
explore_cell(2, 3)  # Evaluative × Consistency
```

---

## Migration from Previous Versions

### From v14.x Framework Architecture

The v15.0.0 semantic calculator is a **complete rewrite**. Key changes:

**Old (v14.x):**
```python
# Old framework approach - extensible, complex
from chirality import S1Runner, S2Runner, S3Runner, OpenAIResolver
from chirality.core.serialize import load_matrix

s1 = S1Runner(OpenAIResolver())
results = s1.run({"A": matrix_a, "B": matrix_b})
```

**New (v15.0.0):**
```python
# New semantic calculator - direct, simple  
from chirality import compute_matrix_C, CellResolver, MATRIX_A, MATRIX_B

resolver = CellResolver()
C = compute_matrix_C(MATRIX_A, MATRIX_B, resolver, valley_summary)
```

**Migration Steps:**
1. **Replace S1/S2/S3 runners** with direct `compute_*` functions
2. **Replace OpenAIResolver** with `CellResolver` 
3. **Use canonical matrices** (`MATRIX_A`, `MATRIX_B`, `MATRIX_J`) instead of JSON files
4. **Update import paths** - all core functions now in `chirality` top-level
5. **Replace matrix serialization** with direct matrix objects

---

## Performance Considerations

### Optimization Strategies

```python
# 1. Use echo resolver for development/testing
echo_resolver = EchoResolver()  # No API calls, instant results

# 2. Implement caching for repeated computations  
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_compute_cell(row, col, resolver_type, valley_hash):
    # Cache expensive computations
    pass

# 3. Batch API calls when possible
# CellResolver automatically batches within single matrix computation

# 4. Monitor API usage
with JSONLTracer() as tracer:
    cell = compute_cell_C(0, 0, A, B, resolver, valley, tracer)
    # Analyze trace file for API call patterns and latency
```

### Memory Management

```python
# For large batch processing, process matrices in chunks
def process_matrix_chunked(A, B, resolver, valley, chunk_size=4):
    total_cells = A.shape[0] * B.shape[1]  # 3 × 4 = 12 for canonical matrices
    
    for start in range(0, total_cells, chunk_size):
        end = min(start + chunk_size, total_cells)
        
        # Process chunk of cells
        for idx in range(start, end):
            row = idx // B.shape[1] 
            col = idx % B.shape[1]
            cell = compute_cell_C(row, col, A, B, resolver, valley)
            yield cell
```

---

## Best Practices

### 1. Always Use Canonical Matrices
```python
# ✅ Good - use provided canonical matrices
from chirality import MATRIX_A, MATRIX_B, MATRIX_J

# ❌ Avoid - creating custom matrices breaks semantic coherence
custom_matrix = Matrix(...)  # Loses ontological foundation
```

### 2. Validate Inputs Before Operations
```python
from chirality import validate_matrix, CF14ValidationError

errors = validate_matrix(MATRIX_A)
if errors:
    raise CF14ValidationError(f"Invalid matrix: {errors}")
```

### 3. Use Appropriate Resolvers  
```python
# Development/Testing: Use echo resolver
echo_resolver = EchoResolver()

# Production: Use OpenAI resolver with error handling
try:
    resolver = CellResolver(api_key=api_key)
except ValueError:
    print("OpenAI API key required for production use")
    resolver = EchoResolver()  # Fallback to echo
```

### 4. Enable Tracing for Debugging
```python
# Always use tracing when developing or debugging
with JSONLTracer(thread_id="debug") as tracer:
    cell = compute_cell_C(0, 0, A, B, resolver, valley, tracer)
    # Examine traces/debug/ for detailed pipeline execution
```

### 5. Proper Resource Management
```python
# Use context managers for automatic cleanup
with JSONLTracer() as tracer:
    with Neo4jWorkingMemoryExporter() as exporter:
        cell = compute_cell_C(0, 0, A, B, resolver, valley, tracer, exporter)
        # Resources automatically closed
```

---

## Version Compatibility

**Current Version:** 15.0.0

**Python Compatibility:** 3.9, 3.10, 3.11, 3.12, 3.13

**Dependencies:**
- **Required**: `click>=8.0.0`, `python-dotenv>=1.0.0` 
- **Optional**: `openai>=1.0.0` (for CellResolver), `neo4j>=5.0.0` (for working memory export)

**Installation Matrix:**
```bash
# Minimal (echo resolver only)
pip install chirality-framework==15.0.0

# With OpenAI support  
pip install chirality-framework[openai]==15.0.0

# With Neo4j working memory
pip install chirality-framework[neo4j]==15.0.0

# Full installation
pip install chirality-framework[all]==15.0.0
```

---

This comprehensive API reference covers all public interfaces, usage patterns, and best practices for the CF14 Semantic Calculator. The API is designed for both interactive exploration and production integration, with complete observability and robust error handling throughout.
