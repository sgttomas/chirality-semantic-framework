#!/usr/bin/env python3
"""
CLI for CF14 Semantic Calculator.

Provides direct access to the 3-stage pipeline for debugging and observability.
Focus on the compute-cell command which shows the complete transformation
from mechanical k-products through semantic resolution to ontological lensing.
"""

import click
import json
import sys
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file in project root
load_dotenv(override=True)

# Import core components
from .core.types import Cell, Matrix
from .core.context import SemanticContext
from .core.matrices import MATRIX_A, MATRIX_B, MATRIX_J
from .core.operations import (
    compute_cell_C,
    compute_cell_F,
    synthesize_cell_D,
    compute_matrix_C,
    compute_matrix_F,
    synthesize_matrix_D
)
from .core.cell_resolver import CellResolver
from .core.resolvers import EchoResolver
from .exporters.working_memory_exporter import Neo4jWorkingMemoryExporter
from .core.tracer import JSONLTracer

# Click styling for better output
STAGE_STYLE = {"fg": "cyan", "bold": True}
SUCCESS_STYLE = {"fg": "green", "bold": True}
ERROR_STYLE = {"fg": "red", "bold": True}
INFO_STYLE = {"fg": "yellow"}
DIM_STYLE = {"dim": True}


@click.group()
@click.version_option(version="15.0.0", prog_name="Chirality Framework")
def cli():
    """
    Chirality Framework - CF14 Semantic Calculator
    
    A fixed, canonical algorithm for structured problem-solving through
    a 3-stage semantic interpretation pipeline:
    
    \b
    Stage 1 (Combinatorial): Mechanical k-product generation
    Stage 2 (Semantic): LLM resolution of word pairs
    Stage 3 (Lensing): Ontological interpretation through coordinates
    
    Use 'compute-cell' to debug individual cells through the pipeline.
    """
    pass


@cli.command()
@click.argument('matrix', type=click.Choice(['C', 'F', 'D'], case_sensitive=False))
@click.option('--i', 'row', type=click.IntRange(0, 2), required=True, 
              help='Row index (0-2)')
@click.option('--j', 'col', type=click.IntRange(0, 3), required=True,
              help='Column index (0-3)')
@click.option('--verbose', '-v', is_flag=True,
              help='Show intermediate results from each stage')
@click.option('--resolver', type=click.Choice(['echo', 'openai'], case_sensitive=False),
              default='echo', help='Resolver to use (default: echo for testing)')
@click.option('--api-key', envvar='OPENAI_API_KEY',
              help='OpenAI API key (or set OPENAI_API_KEY env var)')
@click.option('--trace/--no-trace', default=False,
              help='Enable JSONL tracing to traces/ directory')
@click.option('--neo4j-export/--no-neo4j-export', default=False,
              help='Enable writing output to Neo4j.')
@click.option('--problem', default="generating reliable knowledge",
              help='Problem statement for D matrix synthesis')
def compute_cell(matrix: str, row: int, col: int, verbose: bool, 
                resolver: str, api_key: Optional[str], trace: bool, neo4j_export: bool, problem: str):
    """
    Compute a single cell through the 3-stage pipeline.
    
    \b
    Examples:
        chirality compute-cell C --i 0 --j 0 -v
        chirality compute-cell F --i 1 --j 2 --verbose
        chirality compute-cell D --i 2 --j 1 --problem "creating value"
    """
    resolver_obj = None
    tracer_obj = None
    exporter_obj = None

    try:
        # Setup resolver
        if resolver == 'openai':
            if not api_key:
                click.echo(click.style(
                    "Error: OpenAI API key required. Set OPENAI_API_KEY or use --api-key",
                    **ERROR_STYLE
                ))
                sys.exit(1)
            resolver_obj = CellResolver(api_key=api_key)
            click.echo(click.style("Using OpenAI resolver", **INFO_STYLE))
        else:
            class EchoResolverAdapter:
                def resolve_semantic_pair(self, pair: str, context: SemanticContext) -> str:
                    if " * " in pair:
                        left, right = pair.split(" * ", 1)
                        return f"{right} {left}"
                    return f"Resolved({pair})"
                def apply_ontological_lens(self, content: str, context: SemanticContext) -> str:
                    return f"By applying {context.row_label} lens through {context.col_label} coordinates: {content}"
            resolver_obj = EchoResolverAdapter()
            click.echo(click.style("Using Echo resolver (deterministic mock)", **INFO_STYLE))
        
        # Setup tracer and exporter
        tracer_obj = JSONLTracer() if trace else None
        if trace:
            click.echo(click.style("Tracing enabled -> traces/", **INFO_STYLE))
        
        exporter_obj = Neo4jWorkingMemoryExporter() if neo4j_export else None
        if neo4j_export:
            click.echo(click.style("Neo4j export enabled", **INFO_STYLE))

        # Get canonical matrices and context
        A, B, J = MATRIX_A, MATRIX_B, MATRIX_J
        valley_summary = "Problem Statement -> [Requirements] -> Objectives -> Solution Objectives"
        
        click.echo()
        click.echo(click.style(f"Computing {matrix}[{row},{col}]", **STAGE_STYLE))
        click.echo(click.style("=" * 50, **DIM_STYLE))
        
        # Compute the requested cell based on matrix type
        if matrix.upper() == 'C':
            if verbose: # Verbose mode is not implemented for this flow yet
                cell = compute_cell_C(row, col, A, B, resolver_obj, valley_summary, tracer_obj, exporter_obj)
                _show_cell_result(cell, A.row_labels[row], B.col_labels[col])
            else:
                cell = compute_cell_C(row, col, A, B, resolver_obj, valley_summary, tracer_obj, exporter_obj)
                _show_cell_result(cell, A.row_labels[row], B.col_labels[col])
                
        elif matrix.upper() == 'F':
            C = compute_matrix_C(A, B, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            if verbose: # Verbose mode is not implemented for this flow yet
                cell = compute_cell_F(row, col, J, C, resolver_obj, valley_summary, tracer_obj, exporter_obj)
                _show_cell_result(cell, J.row_labels[row], J.col_labels[col])
            else:
                cell = compute_cell_F(row, col, J, C, resolver_obj, valley_summary, tracer_obj, exporter_obj)
                _show_cell_result(cell, J.row_labels[row], J.col_labels[col])
                
        elif matrix.upper() == 'D':
            C = compute_matrix_C(A, B, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            F = compute_matrix_F(J, C, resolver_obj, valley_summary, tracer_obj, exporter_obj)
            if verbose: # Verbose mode is not implemented for this flow yet
                cell = synthesize_cell_D(row, col, A, F, problem, resolver_obj, valley_summary, tracer_obj, exporter_obj)
                _show_cell_result(cell, A.row_labels[row], A.col_labels[col])
            else:
                cell = synthesize_cell_D(row, col, A, F, problem, resolver_obj, valley_summary, tracer_obj, exporter_obj)
                _show_cell_result(cell, A.row_labels[row], A.col_labels[col])
            
    except Exception as e:
        click.echo(click.style(f"Error: {e}", **ERROR_STYLE))
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    finally:
        # Safely close connections
        if tracer_obj:
            tracer_obj.close()
            click.echo(click.style("✓ Trace file closed.", **DIM_STYLE))
        if exporter_obj:
            exporter_obj.close()
            click.echo(click.style("✓ Neo4j connection closed.", **DIM_STYLE))


def _show_c_computation_verbose(row: int, col: int, A: Matrix, B: Matrix, 
                                resolver, valley_summary: str, tracer):
    """Show verbose output for C matrix cell computation."""
    click.echo()
    click.echo(click.style("STAGE 1: Combinatorial (Mechanical)", **STAGE_STYLE))
    click.echo(click.style("-" * 40, **DIM_STYLE))
    
    # Stage 1: Generate k-products
    raw_products = []
    for k in range(A.shape[1]):
        a_cell = A.get_cell(row, k)
        b_cell = B.get_cell(k, col)
        product = f"{a_cell.value} * {b_cell.value}"
        raw_products.append(product)
        click.echo(f"  k={k}: {product}")
    
    click.echo()
    click.echo(click.style("STAGE 2: Semantic Resolution (LLM)", **STAGE_STYLE))
    click.echo(click.style("-" * 40, **DIM_STYLE))
    
    # Stage 2: Resolve each pair
    resolved = []
    for k, product in enumerate(raw_products):
        context = SemanticContext(
            station_context="Requirements",
            valley_summary=valley_summary,
            row_label=A.row_labels[row],
            col_label=B.col_labels[col],
            operation_type="*",
            terms={"pair": product},
            matrix="C",
            i=row,
            j=col
        )
        concept = resolver.resolve_semantic_pair(product, context)
        resolved.append(concept)
        click.echo(f"  {product} → {click.style(concept, fg='green')}")
    
    click.echo()
    click.echo(click.style("STAGE 3: Ontological Lensing", **STAGE_STYLE))
    click.echo(click.style("-" * 40, **DIM_STYLE))
    
    # Stage 3: Apply lens
    combined = ", ".join(resolved)
    click.echo(f"  Combined: {combined[:80]}...")
    click.echo(f"  Row lens: {A.row_labels[row]}")
    click.echo(f"  Col lens: {B.col_labels[col]}")
    
    context = SemanticContext(
        station_context="Requirements",
        valley_summary=valley_summary,
        row_label=A.row_labels[row],
        col_label=B.col_labels[col],
        operation_type="interpret",
        terms={"content": combined},
        matrix="C",
        i=row,
        j=col
    )
    final = resolver.apply_ontological_lens(combined, context)
    
    click.echo()
    click.echo(click.style("FINAL RESULT:", **SUCCESS_STYLE))
    click.echo(click.style("-" * 40, **DIM_STYLE))
    click.echo(f"  {final}")


def _show_cell_result(cell: Cell, row_label: str, col_label: str):
    """Show the final cell result and provenance."""
    click.echo()
    click.echo(click.style("Result:", **SUCCESS_STYLE))
    click.echo(f"  Coordinates: ({row_label}, {col_label})")
    click.echo(f"  Value: {cell.value}")
    
    click.echo()
    click.echo(click.style("Provenance:", **INFO_STYLE))
    _show_provenance(cell.provenance)


def _show_provenance(provenance: dict, indent: int = 2):
    """Pretty print provenance dictionary."""
    for key, value in provenance.items():
        if isinstance(value, list) and len(value) > 3:
            # Abbreviate long lists
            click.echo(f"{' ' * indent}{key}: [{len(value)} items]")
            for item in value[:2]:
                click.echo(f"{' ' * (indent + 2)}- {item}")
            click.echo(f"{' ' * (indent + 2)}... ({len(value) - 2} more)")
        else:
            click.echo(f"{' ' * indent}{key}: {value}")


@cli.command()
def info():
    """
    Display information about the CF14 semantic calculator.
    """
    click.echo(click.style("Chirality Framework - CF14 Semantic Calculator", **STAGE_STYLE))
    click.echo(click.style("=" * 50, **DIM_STYLE))
    click.echo()
    click.echo("Version: 15.0.0")
    click.echo("Algorithm: 3-stage semantic interpretation pipeline")
    click.echo()
    click.echo(click.style("Canonical Matrices:", **INFO_STYLE))
    click.echo("  A: 3×4 (Axioms/Problem Statement)")
    click.echo("  B: 4×4 (Bridge)")
    click.echo("  J: 3×4 (Judgment)")
    click.echo()
    click.echo(click.style("Result Matrices:", **INFO_STYLE))
    click.echo("  C = A * B: Requirements (3×4)")
    click.echo("  F = J ⊙ C: Objectives (3×4)")
    click.echo("  D = synthesis(A, F): Solution Objectives (3×4)")
    click.echo()
    click.echo(click.style("3-Stage Pipeline:", **INFO_STYLE))
    click.echo("  Stage 1: Combinatorial (mechanical k-products)")
    click.echo("  Stage 2: Semantic (LLM pair resolution)")
    click.echo("  Stage 3: Lensing (ontological interpretation)")
    click.echo()
    click.echo("Use 'chirality compute-cell --help' for debugging individual cells")


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == '__main__':
    cli()