"""
Tests for the CF14 3-stage semantic pipeline operations.

Tests each stage independently and the complete pipeline end-to-end,
using mock resolvers to ensure fast, deterministic, offline testing.
"""

import pytest
from typing import List

# Add parent directory to path for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from chirality.core.operations import (
    compute_cell_C,
    compute_cell_F,
    synthesize_cell_D,
    compute_matrix_C,
    compute_matrix_F,
    synthesize_matrix_D
)
from chirality.core.context import SemanticContext
from tests.mocks import (
    MockCellResolver,
    MockTracer,
    MockMatrix,
    create_test_matrices
)


class TestStage1Combinatorial:
    """Test Stage 1: Mechanical k-product generation (no LLM)."""
    
    def test_k_products_generation(self):
        """Test that k-products are generated correctly without LLM calls."""
        A, B = create_test_matrices()
        resolver = MockCellResolver()
        
        # Compute C[0,0] = A[0,:] dot B[:,0]
        cell = compute_cell_C(0, 0, A, B, resolver, "Test valley")
        
        # Check provenance contains correct k-products
        expected_products = [
            "Values * Necessary",
            "Actions * Contingent", 
            "Benchmarks * Fundamental",
            "Feedback * Best Practices"
        ]
        
        assert "stage_1_products" in cell.provenance
        assert cell.provenance["stage_1_products"] == expected_products
    
    def test_no_llm_calls_for_combinatorial(self):
        """Verify Stage 1 generates products mechanically without resolver calls."""
        A, B = create_test_matrices()
        resolver = MockCellResolver()
        
        # The combinatorial stage shouldn't call the resolver at all
        # We'll verify this by checking call counts after they're added
        
        # For now, verify products are generated
        cell = compute_cell_C(1, 1, A, B, resolver, "Test valley")
        
        expected_products = [
            "Processes * Sufficient",
            "Decisions * Dependent",
            "Standards * Essential",
            "Outcomes * Guidelines"
        ]
        
        assert cell.provenance["stage_1_products"] == expected_products
    
    def test_k_products_for_different_cells(self):
        """Test k-product generation for various cell positions."""
        A, B = create_test_matrices()
        resolver = MockCellResolver()
        
        # Test C[2,3] = A[2,:] dot B[:,3]
        cell = compute_cell_C(2, 3, A, B, resolver, "Test valley")
        
        expected_products = [
            "Insights * Optimal",
            "Operations * Variable",
            "Metrics * Core",
            "Learning * Methods"
        ]
        
        assert cell.provenance["stage_1_products"] == expected_products


class TestStage2SemanticResolution:
    """Test Stage 2: Semantic pair resolution (with mock LLM)."""
    
    def test_semantic_pair_resolution(self):
        """Test that word pairs are resolved into concepts."""
        resolver = MockCellResolver()
        context = SemanticContext(
            station_context="Requirements",
            valley_summary="Test valley",
            row_label="Normative",
            col_label="Possibility",
            operation_type="*",
            terms={"pair": "Values * Necessary"},
            matrix="C",
            i=0,
            j=0
        )
        
        result = resolver.resolve_semantic_pair("Values * Necessary", context)
        assert result == "Essential Values"
    
    def test_all_pairs_resolved(self):
        """Test that all k-products get resolved in Stage 2."""
        A, B = create_test_matrices()
        resolver = MockCellResolver()
        
        cell = compute_cell_C(0, 0, A, B, resolver, "Test valley")
        
        # Check Stage 2 resolved concepts
        expected_resolved = [
            "Essential Values",
            "Conditional Actions",
            "Foundational Benchmarks",
            "Optimal Reference Points"
        ]
        
        assert "stage_2_resolved" in cell.provenance
        assert cell.provenance["stage_2_resolved"] == expected_resolved
    
    def test_unknown_pair_handling(self):
        """Test resolution of pairs not in predefined patterns."""
        resolver = MockCellResolver(pattern_style="descriptive")
        context = SemanticContext(
            station_context="Requirements",
            valley_summary="Test valley",
            row_label="Operative",
            col_label="Challenge",
            operation_type="*",
            terms={"pair": "Unknown * Concept"},
            matrix="C",
            i=1,
            j=1
        )
        
        result = resolver.resolve_semantic_pair("Unknown * Concept", context)
        assert result == "Concept Unknown"  # Descriptive style reverses order


class TestStage3OntologicalLensing:
    """Test Stage 3: Ontological interpretation through row/column context."""
    
    def test_ontological_lens_application(self):
        """Test that row/column context is applied for interpretation."""
        resolver = MockCellResolver()
        context = SemanticContext(
            station_context="Requirements",
            valley_summary="Test valley",
            row_label="Normative",
            col_label="Determinacy",
            operation_type="interpret",
            terms={"content": "Essential Values, Conditional Actions"},
            matrix="C",
            i=0,
            j=0
        )
        
        result = resolver.apply_ontological_lens(
            "Essential Values, Conditional Actions",
            context
        )
        
        # Verify interpretation includes row/column context
        assert "Normative" in result or "establishing standards" in result
        assert "Determinacy" in result or "defining clear boundaries" in result
    
    def test_complete_lensing_in_pipeline(self):
        """Test Stage 3 produces final interpreted meaning."""
        A, B = create_test_matrices()
        resolver = MockCellResolver()
        
        cell = compute_cell_C(0, 0, A, B, resolver, "Test valley")
        
        # Check final lensed result
        assert "stage_3_lensed" in cell.provenance
        assert cell.value == cell.provenance["stage_3_lensed"]
        
        # Final value should include interpretation
        assert "interpret" in cell.value.lower() or "establishing" in cell.value.lower()


class TestCompletePipeline:
    """Test the complete 3-stage pipeline end-to-end."""
    
    def test_all_three_stages_present(self):
        """Verify all three stages are executed and recorded."""
        A, B = create_test_matrices()
        resolver = MockCellResolver()
        
        cell = compute_cell_C(0, 0, A, B, resolver, "Test valley")
        
        # Verify all stages in provenance
        assert "stage_1_products" in cell.provenance
        assert "stage_2_resolved" in cell.provenance
        assert "stage_3_lensed" in cell.provenance
        assert "operation" in cell.provenance
        assert cell.provenance["operation"] == "compute_C"
    
    def test_pipeline_with_tracing(self):
        """Test complete pipeline with tracer capturing all stages."""
        A, B = create_test_matrices()
        resolver = MockCellResolver()
        tracer = MockTracer()
        
        cell = compute_cell_C(0, 0, A, B, resolver, "Test valley", tracer)
        
        # Verify tracer captured all stages
        assert tracer.verify_complete_pipeline()
        
        # Check specific stage events
        combinatorial_events = tracer.find_events_by_stage("combinatorial")
        assert len(combinatorial_events) >= 1
        
        semantic_events = tracer.find_events_by_stage("product:k=")
        assert len(semantic_events) == 4  # 4 k-products for matrix multiplication
        
        final_events = tracer.find_events_by_stage("final")
        assert len(final_events) == 1
    
    def test_coordinates_preserved(self):
        """Test that ontological coordinates are preserved throughout."""
        A, B = create_test_matrices()
        resolver = MockCellResolver()
        
        cell = compute_cell_C(1, 2, A, B, resolver, "Test valley")
        
        # Check coordinates in provenance
        assert "coordinates" in cell.provenance
        expected_coords = f"({A.row_labels[1]}, {B.col_labels[2]})"
        assert cell.provenance["coordinates"] == expected_coords
        
        # Verify cell position
        assert cell.row == 1
        assert cell.col == 2
    
    def test_different_operation_types(self):
        """Test F and D operations use appropriate stages."""
        A, B = create_test_matrices()
        J, C = create_test_matrices()  # Reuse for testing
        resolver = MockCellResolver()
        
        # Test compute_cell_F (element-wise)
        cell_f = compute_cell_F(0, 0, J, C, resolver, "Test valley")
        assert "stage_1_element_wise" in cell_f.provenance
        assert "stage_2_resolved" in cell_f.provenance
        assert "stage_3_lensed" in cell_f.provenance
        
        # Test synthesize_cell_D (synthesis)
        cell_d = synthesize_cell_D(0, 0, A, C, "test problem", resolver, "Test valley")
        assert "stage_1_synthesis" in cell_d.provenance
        assert "stage_2_lensed" in cell_d.provenance
        assert "problem" in cell_d.provenance


class TestMatrixOperations:
    """Test matrix-level wrapper functions."""
    
    def test_compute_matrix_C(self):
        """Test full matrix C computation."""
        A, B = create_test_matrices()
        resolver = MockCellResolver()
        
        matrix_C = compute_matrix_C(A, B, resolver, "Test valley")
        
        assert matrix_C.name == "C"
        assert matrix_C.station == "Requirements"
        assert len(matrix_C.cells) == 3  # 3 rows
        assert len(matrix_C.cells[0]) == 4  # 4 columns
        
        # Verify all cells computed
        for i in range(3):
            for j in range(4):
                cell = matrix_C.cells[i][j]
                assert cell.row == i
                assert cell.col == j
                assert len(cell.value) > 0
    
    def test_compute_matrix_F(self):
        """Test full matrix F computation."""
        J, C = create_test_matrices()
        resolver = MockCellResolver()
        
        matrix_F = compute_matrix_F(J, C, resolver, "Test valley")
        
        assert matrix_F.name == "F"
        assert matrix_F.station == "Objectives"
        assert matrix_F.cells[0][0].provenance["operation"] == "compute_F"
    
    def test_synthesize_matrix_D(self):
        """Test full matrix D synthesis."""
        A, F = create_test_matrices()
        resolver = MockCellResolver()
        
        matrix_D = synthesize_matrix_D(A, F, "generating knowledge", resolver, "Test valley")
        
        assert matrix_D.name == "D"
        assert matrix_D.station == "Objectives"
        
        # Check synthesis formula was applied
        cell = matrix_D.cells[0][0]
        assert "generating knowledge" in cell.provenance["stage_1_synthesis"]


class TestResolverCallCounts:
    """Test that resolvers are called the expected number of times."""
    
    def test_resolver_call_efficiency(self):
        """Verify resolver is called efficiently without redundancy."""
        A, B = create_test_matrices()
        resolver = MockCellResolver()
        
        # Reset counts
        resolver.reset_call_counts()
        
        # Compute one cell
        cell = compute_cell_C(0, 0, A, B, resolver, "Test valley")
        
        counts = resolver.get_call_counts()
        
        # Should call resolve_semantic_pair once per k-product (4 times)
        assert counts["resolve_semantic_pair"] == 4
        
        # Should call apply_ontological_lens once for final interpretation
        assert counts["apply_ontological_lens"] == 1
    
    def test_matrix_computation_call_counts(self):
        """Test call counts for full matrix computation."""
        A, B = create_test_matrices()
        resolver = MockCellResolver()
        resolver.reset_call_counts()
        
        matrix_C = compute_matrix_C(A, B, resolver, "Test valley")
        
        counts = resolver.get_call_counts()
        
        # 3x4 matrix, 4 k-products each = 12*4 = 48 semantic resolutions
        assert counts["resolve_semantic_pair"] == 48
        
        # 3x4 matrix = 12 lens applications
        assert counts["apply_ontological_lens"] == 12


if __name__ == "__main__":
    pytest.main([__file__, "-v"])