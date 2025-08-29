# Neo4j Query Cookbook

This document provides a set of practical Cypher queries to explore and analyze the "working memory" of the Chirality Framework stored in the Neo4j database. The graph is created by the `Neo4jWorkingMemoryExporter` when you use the `--neo4j-export` flag.

## The Graph Schema

The graph model is simple and designed for traceability:

*   **Nodes:**
    *   `(:Matrix {name, station})`: Represents a matrix like C, F, or D.
    *   `(:Cell {id, row, col, value, ...})`: Represents a single computed cell. Its `id` is a composite key like `C-0-1`.
    *   `(:Stage)`: Represents a step in the 3-stage pipeline. It has sub-labels like `:Combinatorial`, `:Semantic`, or `:Lensed` and contains the intermediate data for that stage.

*   **Relationships:**
    *   `(:Matrix)-[:CONTAINS]->(:Cell)`
    *   `(:Cell)-[:HAS_STAGE]->(:Stage)`

---

## Query Recipes

### 1. Find a Specific Cell

**Question:** How do I find the final computed value for cell D(2,1)?

```cypher
MATCH (c:Cell {id: 'D-2-1'})
RETURN c.value, c.row_label, c.col_label
```

### 2. Trace the Full History of a Single Cell

**Question:** How was the final value for cell C(0,0) created? Show me all the stages.

```cypher
MATCH (c:Cell {id: 'C-0-0'})-[:HAS_STAGE]->(s:Stage)
RETURN s
ORDER BY s.timestamp
```
*This will return the `:Combinatorial`, `:Semantic`, and `:Lensed` stage nodes for that cell, allowing you to see the full transformation.* 

### 3. See All Cells in a Matrix

**Question:** Show me the final values for all cells in Matrix F.

```cypher
MATCH (m:Matrix {name: 'F'})-[:CONTAINS]->(c:Cell)
RETURN c.row, c.col, c.value
ORDER BY c.row, c.col
```

### 4. Find Cells with Specific Provenance

**Question:** Find all cells where the semantic resolution (Stage 2) involved the concept "Guiding Imperatives".

```cypher
MATCH (c:Cell)-[:HAS_STAGE]->(s:Stage:Semantic)
WHERE 'Guiding Imperatives' IN s.concepts
RETURN c.id, c.value
```

### 5. Analyze the Raw Inputs for a Cell

**Question:** What were the raw, mechanical products generated for cell C(1,2) before any LLM calls?

```cypher
MATCH (c:Cell {id: 'C-1-2'})-[:HAS_STAGE]->(s:Stage:Combinatorial)
RETURN s.products
```
