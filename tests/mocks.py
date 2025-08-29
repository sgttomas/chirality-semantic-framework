"""
Mock implementations for testing the CF14 semantic calculator.

Provides deterministic, predictable resolvers that don't require LLM calls,
enabling fast, offline testing of the 3-stage pipeline.
"""

from typing import Dict, Any
from chirality.core.context import SemanticContext


class MockCellResolver:
    """
    Deterministic resolver for testing the 3-stage pipeline.
    
    Returns predictable outputs based on input patterns, allowing us to
    test the pipeline mechanics without OpenAI API calls.
    """
    
    def __init__(self, pattern_style: str = "descriptive"):
        """
        Initialize mock resolver.
        
        Args:
            pattern_style: Style of mock responses
                - "descriptive": Human-readable descriptions
                - "mechanical": Technical/mechanical style
                - "minimal": Shortest possible valid responses
        """
        self.pattern_style = pattern_style
        self.call_count = {
            "resolve_semantic_pair": 0,
            "apply_ontological_lens": 0
        }
    
    def resolve_semantic_pair(self, pair: str, context: SemanticContext) -> str:
        """
        Mock semantic resolution for Stage 2.
        
        Returns predictable concept based on input pair.
        """
        self.call_count["resolve_semantic_pair"] += 1
        
        # Deterministic patterns for common test cases
        patterns = {
            "Values * Necessary": "Essential Values",
            "Actions * Contingent": "Conditional Actions",
            "Benchmarks * Fundamental": "Foundational Benchmarks",
            "Feedback * Best Practices": "Optimal Reference Points",
            "Processes * Necessary": "Required Processes",
            "Insights * Necessary": "Critical Insights",
            "Comparisons * Necessary": "Essential Comparisons",
            "Learning * Necessary": "Fundamental Learning",
            # Pattern matching for unknown pairs
        }
        
        # Check for exact match
        if pair in patterns:
            return patterns[pair]
        
        # Generate predictable output for unknown pairs
        if " * " in pair:
            left, right = pair.split(" * ", 1)
            if self.pattern_style == "minimal":
                return f"{left[:3]}{right[:3]}"
            elif self.pattern_style == "mechanical":
                return f"[{left}×{right}]"
            else:  # descriptive
                return f"{right} {left}"
        
        return f"Resolved({pair})"
    
    def apply_ontological_lens(self, content: str, context: SemanticContext) -> str:
        """
        Mock ontological lensing for Stage 3.
        
        Applies row/column context to interpret content.
        """
        self.call_count["apply_ontological_lens"] += 1
        
        # Build interpretation based on ontological coordinates
        row_interpretations = {
            "Normative": "establishing standards for",
            "Operative": "implementing processes for", 
            "Evaluative": "assessing quality of"
        }
        
        col_interpretations = {
            "Determinacy": "defining clear boundaries",
            "Sufficiency": "ensuring completeness",
            "Necessity": "identifying requirements",
            "Contingency": "managing dependencies",
            "Possibility": "exploring potential",
            "Challenge": "addressing difficulties",
            "Comparison": "evaluating alternatives",
            "Paradigm": "shifting perspectives"
        }
        
        # Get row/col modifiers
        row_modifier = row_interpretations.get(
            context.row_label, 
            f"applying {context.row_label}"
        )
        col_modifier = col_interpretations.get(
            context.col_label,
            f"through {context.col_label}"
        )
        
        if self.pattern_style == "minimal":
            return f"{content} ({context.row_label[:3]}/{context.col_label[:3]})"
        elif self.pattern_style == "mechanical":
            return f"[{context.row_label}|{context.col_label}]:{content}"
        else:  # descriptive
            return f"By {row_modifier} and {col_modifier}, we interpret: {content}"
    
    def reset_call_counts(self):
        """Reset call counters for fresh test."""
        self.call_count = {
            "resolve_semantic_pair": 0,
            "apply_ontological_lens": 0
        }
    
    def get_call_counts(self) -> Dict[str, int]:
        """Get current call counts for assertions."""
        return self.call_count.copy()


class MockTracer:
    """
    Mock tracer for testing without file I/O.
    
    Captures trace events in memory for verification.
    """
    
    def __init__(self):
        self.events = []
        self.stages_traced = set()
    
    def trace_stage(self, stage_type: str, context: Any, result: Any, extras: Dict[str, Any] = None):
        """
        Capture trace event in memory.
        
        Args:
            stage_type: Type of stage being traced
            context: SemanticContext or similar
            result: Result dictionary with text, terms_used, warnings
            extras: Additional metadata
        """
        event = {
            "stage": stage_type,
            "context": context,
            "result": result,
            "extras": extras or {}
        }
        self.events.append(event)
        self.stages_traced.add(stage_type)
    
    def get_events(self):
        """Get all traced events."""
        return self.events
    
    def get_stages_traced(self):
        """Get unique stages that were traced."""
        return self.stages_traced
    
    def reset(self):
        """Clear all captured events."""
        self.events = []
        self.stages_traced = set()
    
    def find_events_by_stage(self, stage_pattern: str):
        """Find all events matching a stage pattern."""
        return [e for e in self.events if stage_pattern in e["stage"]]
    
    def verify_complete_pipeline(self) -> bool:
        """
        Verify that a complete 3-stage pipeline was traced.
        
        Returns:
            True if combinatorial, semantic, and lensing stages all present
        """
        expected_stages = {"combinatorial", "product:k=", "final"}
        for stage in expected_stages:
            if not any(stage in s for s in self.stages_traced):
                return False
        return True


class MockMatrix:
    """
    Simple mock matrix for testing without loading full canonical matrices.
    """
    
    def __init__(self, name: str, rows: int = 3, cols: int = 4):
        self.name = name
        self.shape = (rows, cols)
        self.row_labels = [f"Row{i}" for i in range(rows)]
        self.col_labels = [f"Col{j}" for j in range(cols)]
        self.cells = []
        
        # Generate simple test cells
        for i in range(rows):
            row_cells = []
            for j in range(cols):
                cell = type('Cell', (), {
                    'row': i,
                    'col': j, 
                    'value': f"{name}[{i},{j}]"
                })()
                row_cells.append(cell)
            self.cells.append(row_cells)
    
    def get_cell(self, i: int, j: int):
        """Get cell at position (i, j)."""
        return self.cells[i][j]


def create_test_matrices():
    """
    Create a standard set of test matrices.
    
    Returns:
        tuple: (A, B) matrices for testing
    """
    A = MockMatrix("A", 3, 4)
    B = MockMatrix("B", 4, 4)
    
    # Set meaningful test values
    test_values_A = [
        ["Values", "Actions", "Benchmarks", "Feedback"],
        ["Processes", "Decisions", "Standards", "Outcomes"],
        ["Insights", "Operations", "Metrics", "Learning"]
    ]
    
    test_values_B = [
        ["Necessary", "Sufficient", "Complete", "Optimal"],
        ["Contingent", "Dependent", "Conditional", "Variable"],
        ["Fundamental", "Essential", "Critical", "Core"],
        ["Best Practices", "Guidelines", "Principles", "Methods"]
    ]
    
    # Apply test values
    for i in range(3):
        for j in range(4):
            A.cells[i][j].value = test_values_A[i][j]
    
    for i in range(4):
        for j in range(4):
            B.cells[i][j].value = test_values_B[i][j]
    
    # Set ontological labels
    A.row_labels = ["Normative", "Operative", "Evaluative"]
    A.col_labels = ["Guiding", "Applying", "Judging", "Reflecting"]
    
    B.row_labels = ["Determinacy", "Sufficiency", "Necessity", "Contingency"]
    B.col_labels = ["Possibility", "Challenge", "Comparison", "Paradigm"]
    
    return A, B