"""
CF14 Three-Stage Cell Pipeline Implementation.

This is the "secret sauce" - the core algorithm that transforms
structural combinations into meaningful semantic insights through
a precise 3-stage interpretation process:

Stage 1 (Combinatorial): Mechanical generation of k-products
Stage 2 (Semantic): LLM resolution of word pairs into concepts  
Stage 3 (Lensing): Ontological interpretation through row/column coordinates

This embodies the "semantic calculator" philosophy: fixed algorithms
that produce predictable, meaningful outputs from canonical inputs.
"""

from typing import List, Optional
from .types import Cell, Matrix
from .context import SemanticContext
from .cell_resolver import CellResolver
from .tracer import JSONLTracer


def compute_cell_C(i: int, j: int, A: Matrix, B: Matrix, resolver: CellResolver, valley_summary: str, tracer: Optional[JSONLTracer] = None) -> Cell:
    """
    Complete 3-stage pipeline for computing C[i,j] = A[i,:] dot B[:,j]
    
    This is the core algorithm that transforms mechanical combinations
    into meaningful semantic insights. Each stage builds on the previous:
    
    Stage 1 (Combinatorial): Generate k-products mechanically (no LLM)
    Stage 2 (Semantic): Resolve word pairs into concepts (LLM)
    Stage 3 (Lensing): Apply ontological interpretation (LLM with deep context)
    
    Args:
        i: Row index in result matrix C
        j: Column index in result matrix C  
        A: Left input matrix (3x4)
        B: Right input matrix (4x4)
        resolver: CellResolver for LLM operations
        valley_summary: Current position in semantic valley
        
    Returns:
        Cell with final semantic result and complete provenance
    """
    
    # Stage 1: Combinatorial (mechanical, no LLM)
    raw_products = []
    for k in range(A.shape[1]):  # A is 3x4, so k goes 0-3
        a_cell = A.get_cell(i, k)
        b_cell = B.get_cell(k, j)
        product_pair = f"{a_cell.value} * {b_cell.value}"
        raw_products.append(product_pair)
    
    # Trace Stage 1 (combinatorial - no LLM call, just mechanical result)
    if tracer:
        stage1_context = SemanticContext(
            station_context="Requirements",
            valley_summary=valley_summary,
            row_label=A.row_labels[i],
            col_label=B.col_labels[j],
            operation_type="combinatorial",
            terms={"products": raw_products},
            matrix="C",
            i=i,
            j=j
        )
        # Tracer expects cell context and result - we'll adapt SemanticContext
        tracer.trace_stage("product:combinatorial", stage1_context, {
            "text": ", ".join(raw_products),
            "terms_used": [f"k={k}" for k in range(len(raw_products))],
            "warnings": []
        }, {
            "station": "Requirements", 
            "valley_summary": valley_summary,
            "products": raw_products
        })

    # Stage 2: Semantic Resolution (LLM resolves each pair)
    resolved_concepts = []
    for k, product_pair in enumerate(raw_products):
        # Create SemanticContext object for this resolution
        context_for_stage2 = SemanticContext(
            station_context="Requirements",
            valley_summary=valley_summary,
            row_label=A.row_labels[i],
            col_label=B.col_labels[j],
            operation_type="*",
            terms={"pair": product_pair},
            matrix="C",
            i=i,
            j=j
        )
        concept = resolver.resolve_semantic_pair(product_pair, context_for_stage2)
        resolved_concepts.append(concept)
        
        # Trace each individual semantic resolution
        if tracer:
            tracer.trace_stage(f"product:k={k}", context_for_stage2, {
                "text": concept,
                "terms_used": product_pair.split(" * "),
                "warnings": []
            }, {
                "station": "Requirements", 
                "valley_summary": valley_summary,
                "products": [product_pair]
            })

    # Stage 3: Lensing (deep ontological interpretation)
    combined_concepts = ", ".join(resolved_concepts)
    # Create SemanticContext object for lensing
    context_for_stage3 = SemanticContext(
        station_context="Requirements",
        valley_summary=valley_summary,
        row_label=A.row_labels[i],
        col_label=B.col_labels[j],
        operation_type="interpret",
        terms={"content": combined_concepts},
        matrix="C",
        i=i,
        j=j
    )
    final_meaning = resolver.apply_ontological_lens(combined_concepts, context_for_stage3)
    
    # Trace Stage 3 (lensing)
    if tracer:
        tracer.trace_stage("final", context_for_stage3, {
            "text": final_meaning,
            "terms_used": resolved_concepts,
            "warnings": []
        }, {
            "station": "Requirements", 
            "valley_summary": valley_summary,
            "stage_plan": ["combinatorial", "semantic", "lensing"]
        })

    return Cell(
        row=i,
        col=j,
        value=final_meaning,
        provenance={
            "stage_1_products": raw_products,
            "stage_2_resolved": resolved_concepts,
            "stage_3_lensed": final_meaning,
            "operation": "compute_C",
            "coordinates": f"({A.row_labels[i]}, {B.col_labels[j]})",
            "traced": tracer is not None
        }
    )


def compute_cell_F(i: int, j: int, J: Matrix, C: Matrix, resolver: CellResolver, valley_summary: str, tracer: Optional[JSONLTracer] = None) -> Cell:
    """
    Element-wise operation F[i,j] = J[i,j] ⊙ C[i,j] with lensing
    
    Since coordinates match, skip combinatorial stage.
    Stage 1: Direct semantic multiplication 
    Stage 2: Apply ontological lens for objectives context
    
    Args:
        i: Row index
        j: Column index
        J: Judgment matrix (3x4)
        C: Composition matrix (3x4)
        resolver: CellResolver for LLM operations
        valley_summary: Current position in semantic valley
        
    Returns:
        Cell with element-wise multiplication result
    """

    # Stage 1: Direct element-wise multiplication (same coordinates)
    j_cell = J.get_cell(i, j)
    c_cell = C.get_cell(i, j)
    element_pair = f"{j_cell.value} * {c_cell.value}"
    
    context_for_stage1 = SemanticContext(
        station_context="Objectives", 
        valley_summary=valley_summary,
        row_label=J.row_labels[i], 
        col_label=J.col_labels[j],
        operation_type="*", 
        terms={"pair": element_pair},
        matrix="F",
        i=i,
        j=j
    )
    resolved_concept = resolver.resolve_semantic_pair(element_pair, context_for_stage1)
    
    # Trace Stage 1 (element-wise semantic resolution)
    if tracer:
        tracer.trace_stage("element-wise", context_for_stage1, {
            "text": resolved_concept,
            "terms_used": element_pair.split(" * "),
            "warnings": []
        }, {
            "station": "Objectives", 
            "valley_summary": valley_summary,
            "products": [element_pair]
        })

    # Stage 2: Apply lens for Objectives station  
    context_for_stage2 = SemanticContext(
        station_context="Objectives", 
        valley_summary=valley_summary,
        row_label=J.row_labels[i], 
        col_label=J.col_labels[j],
        operation_type="interpret", 
        terms={"content": resolved_concept},
        matrix="F",
        i=i,
        j=j
    )
    final_meaning = resolver.apply_ontological_lens(resolved_concept, context_for_stage2)
    
    # Trace Stage 2 (lensing)
    if tracer:
        tracer.trace_stage("final", context_for_stage2, {
            "text": final_meaning,
            "terms_used": [resolved_concept],
            "warnings": []
        }, {
            "station": "Objectives", 
            "valley_summary": valley_summary,
            "stage_plan": ["element-wise", "lensing"]
        })

    return Cell(
        row=i,
        col=j,
        value=final_meaning,
        provenance={
            "stage_1_element_wise": element_pair,
            "stage_2_resolved": resolved_concept,
            "stage_3_lensed": final_meaning,
            "operation": "compute_F",
            "coordinates": f"({J.row_labels[i]}, {J.col_labels[j]})",
            "traced": tracer is not None
        }
    )


def synthesize_cell_D(i: int, j: int, A: Matrix, F: Matrix, problem: str, resolver: CellResolver, valley_summary: str, tracer: Optional[JSONLTracer] = None) -> Cell:
    """
    Synthesis operation using the canonical D formula:
    D[i,j] = A[i,j] + "applied to frame the problem of {problem} and" + F[i,j] + "to resolve the problem"
    
    Stage 1: Apply synthesis formula mechanically
    Stage 2: Apply ontological lens for objectives context
    
    Args:
        i: Row index
        j: Column index
        A: Axioms matrix (3x4)
        F: Functions matrix (3x4)
        problem: Problem statement to synthesize around
        resolver: CellResolver for LLM operations
        valley_summary: Current position in semantic valley
        
    Returns:
        Cell with synthesized solution objective
    """

    # Stage 1: Apply the canonical synthesis formula
    a_cell = A.get_cell(i, j)
    f_cell = F.get_cell(i, j)
    synthesis_statement = f"{a_cell.value} applied to frame the problem of {problem} and {f_cell.value} to resolve the problem"
    
    # Trace Stage 1 (synthesis formula application)
    if tracer:
        stage1_context = SemanticContext(
            station_context="Objectives",
            valley_summary=valley_summary,
            row_label=A.row_labels[i],
            col_label=A.col_labels[j],
            operation_type="synthesis",
            terms={"formula": synthesis_statement, "problem": problem},
            matrix="D",
            i=i,
            j=j
        )
        tracer.trace_stage("synthesis", stage1_context, {
            "text": synthesis_statement,
            "terms_used": [a_cell.value, f_cell.value, problem],
            "warnings": []
        }, {
            "station": "Objectives", 
            "valley_summary": valley_summary,
            "products": [synthesis_statement]
        })

    # Stage 2: Apply lens for Objectives station  
    context_for_stage2 = SemanticContext(
        station_context="Objectives", 
        valley_summary=valley_summary,
        row_label=A.row_labels[i], 
        col_label=A.col_labels[j],  # Note: using A's column labels for D
        operation_type="interpret", 
        terms={"content": synthesis_statement, "problem": problem},
        matrix="D",
        i=i,
        j=j
    )
    final_meaning = resolver.apply_ontological_lens(synthesis_statement, context_for_stage2)
    
    # Trace Stage 2 (lensing)
    if tracer:
        tracer.trace_stage("final", context_for_stage2, {
            "text": final_meaning,
            "terms_used": [synthesis_statement],
            "warnings": []
        }, {
            "station": "Objectives", 
            "valley_summary": valley_summary,
            "stage_plan": ["synthesis", "lensing"]
        })

    return Cell(
        row=i,
        col=j,
        value=final_meaning,
        provenance={
            "stage_1_synthesis": synthesis_statement,
            "stage_2_lensed": final_meaning,
            "operation": "synthesize_D",
            "problem": problem,
            "coordinates": f"({A.row_labels[i]}, {A.col_labels[j]})",
            "traced": tracer is not None
        }
    )


def compute_matrix_C(A: Matrix, B: Matrix, resolver: CellResolver, valley_summary: str, tracer: Optional[JSONLTracer] = None) -> Matrix:
    """
    Convenience wrapper - loops over compute_cell_C. NO semantic logic here.
    
    Simple iteration over the 3x4 result matrix, calling compute_cell_C for each position.
    This follows the "semantic calculator" principle: matrix operations are just
    organized collections of cell operations.
    """
    cells = []
    for i in range(3):  # A is 3x4
        row_cells = []
        for j in range(4):  # B is 4x4, so result is 3x4
            cell = compute_cell_C(i, j, A, B, resolver, valley_summary, tracer)
            row_cells.append(cell)
        cells.append(row_cells)

    return Matrix(
        name="C",
        station="Requirements",
        row_labels=A.row_labels,
        col_labels=B.col_labels,
        cells=cells
    )


def compute_matrix_F(J: Matrix, C: Matrix, resolver: CellResolver, valley_summary: str, tracer: Optional[JSONLTracer] = None) -> Matrix:
    """Convenience wrapper - loops over compute_cell_F"""
    cells = []
    for i in range(3):  # Both J and C are 3x4
        row_cells = []
        for j in range(4):
            cell = compute_cell_F(i, j, J, C, resolver, valley_summary, tracer)
            row_cells.append(cell)
        cells.append(row_cells)

    return Matrix(
        name="F",
        station="Objectives",
        row_labels=J.row_labels,
        col_labels=J.col_labels,
        cells=cells
    )


def synthesize_matrix_D(A: Matrix, F: Matrix, problem: str, resolver: CellResolver, valley_summary: str, tracer: Optional[JSONLTracer] = None) -> Matrix:
    """Convenience wrapper - loops over synthesize_cell_D"""
    cells = []
    for i in range(3):
        row_cells = []
        for j in range(4):
            cell = synthesize_cell_D(i, j, A, F, problem, resolver, valley_summary, tracer)
            row_cells.append(cell)
        cells.append(row_cells)

    return Matrix(
        name="D",
        station="Objectives",
        row_labels=A.row_labels,  # D uses A's row labels
        col_labels=A.col_labels,  # D uses A's col labels
        cells=cells
    )