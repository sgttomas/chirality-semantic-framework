"""
Neo4j Exporter for Chirality Framework "Working Memory".

This module is responsible for persisting the entire semantic journey for each
cell computation to a Neo4j graph database. It captures the final matrices,
the individual cells, and all the intermediate stages of the 3-stage
interpretation pipeline, creating a rich, queryable graph of the process.
"""

import os
from typing import Dict, Any, Optional

from ..core.types import Cell
from ..core.context import SemanticContext

try:
    from neo4j import GraphDatabase, Driver
except ImportError:
    GraphDatabase = None
    Driver = None

class Neo4jWorkingMemoryExporter:
    """Writes the output of cell computations to Neo4j.

    This class implements the logic to map the 3-stage pipeline results
    into a graph structure, connecting matrices, cells, and provenance.
    """

    def __init__(self, uri: str = None, user: str = None, password: str = None):
        if GraphDatabase is None:
            raise ImportError("The 'neo4j' package is required to use the Neo4j exporter. Please install it with `pip install neo4j`.")

        uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = user or os.getenv("NEO4J_USER", "neo4j")
        password = password or os.getenv("NEO4J_PASSWORD", "password")

        self.driver: Driver = GraphDatabase.driver(uri, auth=(user, password))
        self._ensure_schema()

    def _ensure_schema(self):
        """Ensures necessary constraints are created in the database."""
        with self.driver.session() as session:
            # Constraint for Matrices to ensure they are unique by name
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (m:Matrix) REQUIRE m.name IS UNIQUE")
            # Constraint for Cells to ensure they are unique
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (c:Cell) REQUIRE c.id IS UNIQUE")

    def export_cell_computation(self, cell: Cell, context: SemanticContext):
        """Exports the full journey of a single cell computation.

        This method creates a graph representation of the 3-stage pipeline:
        - A (:Matrix) node.
        - A (:Cell) node, linked to its Matrix.
        - A chain of (:Stage) nodes, linked to the Cell, detailing the provenance.
        """
        with self.driver.session() as session:
            # A unique ID for the cell node in the graph
            cell_id = f"{context.matrix}-{cell.row}-{cell.col}"

            # 1. Merge the Matrix node
            session.run(
                "MERGE (m:Matrix {name: $matrix_name}) SET m.station = $station",
                matrix_name=context.matrix,
                station=context.station_context
            )

            # 2. Merge the Cell node and link it to its Matrix
            session.run(
                """
                MATCH (m:Matrix {name: $matrix_name})
                MERGE (c:Cell {id: $cell_id})
                SET
                    c.row = $row,
                    c.col = $col,
                    c.value = $value,
                    c.row_label = $row_label,
                    c.col_label = $col_label
                MERGE (m)-[:CONTAINS]->(c)
                """,
                matrix_name=context.matrix,
                cell_id=cell_id,
                row=cell.row,
                col=cell.col,
                value=cell.value,
                row_label=context.row_label,
                col_label=context.col_label
            )

            # 3. Create and link provenance nodes from the 3-stage pipeline
            provenance = cell.provenance
            if provenance:
                # Stage 1: Combinatorial
                if "stage_1_products" in provenance:
                    session.run(
                        """
                        MATCH (c:Cell {id: $cell_id})
                        CREATE (s:Stage:Combinatorial {products: $products})
                        MERGE (c)-[:HAS_STAGE]->(s)
                        """,
                        cell_id=cell_id,
                        products=provenance["stage_1_products"]
                    )
                # Stage 2: Semantic Resolution
                if "stage_2_resolved" in provenance:
                    session.run(
                        """
                        MATCH (c:Cell {id: $cell_id})
                        CREATE (s:Stage:Semantic {concepts: $concepts})
                        MERGE (c)-[:HAS_STAGE]->(s)
                        """,
                        cell_id=cell_id,
                        concepts=provenance["stage_2_resolved"]
                    )
                # Stage 3: Lensing
                if "stage_3_lensed" in provenance:
                    session.run(
                        """
                        MATCH (c:Cell {id: $cell_id})
                        CREATE (s:Stage:Lensed {meaning: $meaning})
                        MERGE (c)-[:HAS_STAGE]->(s)
                        """,
                        cell_id=cell_id,
                        meaning=provenance["stage_3_lensed"]
                    )

    def close(self):
        """Closes the database connection."""
        if self.driver:
            self.driver.close()
