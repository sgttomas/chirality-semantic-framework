# Prompt Engineering Guide for CF14 Semantic Calculator

**Version: 15.0.0** | **Updated: August 2025**

This guide provides practical methodology for refining the prompts that drive the Three-Stage Interpretation Pipeline. Since semantic quality directly determines the value of the calculator's output, prompt engineering is critical for optimal performance.

## Overview: The Prompt Architecture

The CF14 semantic calculator uses **fragment composition** rather than static templates. The `CellResolver.assemble_prompt()` method dynamically builds prompts from configurable fragments, allowing for systematic refinement and testing.

### Core Prompt Components

1. **System Prompt** (`chirality/core/prompts.py::SYSTEM_PROMPT`)
   - Sets the semantic engine's identity and mission
   - Defines output contract (JSON format requirements)
   - Establishes voice and style guidelines

2. **Operation-Specific Fragments**
   - `resolve_semantic_pair()`: Stage 2 semantic resolution prompts
   - `apply_ontological_lens()`: Stage 3 lensing prompts
   - Each uses dynamic context from `SemanticContext`

3. **Context Injection**
   - Valley position and station context
   - Row and column ontological lenses
   - Operation type and term details

## Stage-Specific Prompt Engineering

### Stage 2: Semantic Resolution (`resolve_semantic_pair`)

**Purpose**: Transform raw word pairs into coherent concepts

**Current Strategy**:
```
"Values * Necessary" → "Essential Values"
"Actions * Contingent" → "Conditional Actions"
```

**Key Prompt Elements**:
- Clear instruction to find **semantic intersection**
- Preserve both term identities
- Aim for **concise expression** (1-3 words preferred)
- Use ontological context (row/column labels)

**Common Issues and Solutions**:

| Problem | Example | Solution |
|---------|---------|----------|
| **Concatenation instead of intersection** | "Values * Necessary" → "Values and Necessary" | Emphasize "semantic intersection" and "fusion of meanings" |
| **Loss of term identity** | "Actions * Contingent" → "Flexibility" | Require that both source concepts remain recognizable |
| **Over-abstraction** | "Benchmarks * Fundamental" → "Measurement Philosophy" | Guide toward concrete, actionable concepts |
| **Inconsistent style** | Mixed formal/informal outputs | Establish clear voice guidelines in system prompt |

### Stage 3: Ontological Lensing (`apply_ontological_lens`)

**Purpose**: Apply deep contextual interpretation through row/column coordinates

**Current Strategy**:
- **Row lens**: Provides the **perspective** (how to approach)
- **Column lens**: Provides the **focus** (what to emphasize)
- **Station context**: Provides the **purpose** (why this matters)

**Effective Lensing Patterns**:
```
Input: "Essential Values, Conditional Actions, Foundational Benchmarks"
Row: "Normative" (establishing standards)
Col: "Necessity" (vs Contingency)
Station: "Requirements"

Output: "To establish normative standards for necessity requirements, we must identify essential values that define quality standards, implement conditional actions that respond to required circumstances, and establish foundational benchmarks that set measurable necessity criteria."
```

**Lensing Quality Indicators**:
- ✅ **Integrates all resolved concepts** from Stage 2
- ✅ **Applies both row and column ontological perspectives**
- ✅ **Provides actionable insight** rather than mere description
- ✅ **Maintains semantic coherence** across the transformation
- ✅ **Appropriate length** (2-3 sentences for stakeholder clarity)

## Manual Refinement Methodology

### 1. **Baseline Testing**
```bash
# Test current prompts with echo resolver (deterministic baseline)
python3 -m chirality.cli compute-cell C --i 0 --j 0 --resolver echo --verbose

# Test with OpenAI resolver (live semantic resolution)
python3 -m chirality.cli compute-cell C --i 0 --j 0 --resolver openai --verbose
```

### 2. **Systematic Testing Matrix**
Test key cells that represent different semantic challenges:

| Cell | Challenge Type | Expected Pattern |
|------|----------------|------------------|
| C[0,0] | Abstract/Concrete combination | Values + Necessity concepts |
| C[1,2] | Process/Outcome integration | Methods + Completeness concepts |
| C[2,3] | Evaluation/Standard alignment | Assessment + Consistency concepts |
| F[0,0] | Element-wise reinforcement | Judgment ⊙ Requirement alignment |
| D[1,1] | Synthesis formula application | Axiom + Function combination |

### 3. **Quality Assessment Criteria**

**Stage 2 Resolution Quality**:
- **Semantic Preservation**: Both input terms recognizable in output
- **Conceptual Coherence**: Result makes intuitive sense
- **Conciseness**: 1-3 words preferred, avoid verbose explanations
- **Consistency**: Similar inputs produce similar output patterns

**Stage 3 Lensing Quality**:
- **Ontological Integration**: Row and column perspectives clearly applied
- **Actionable Insight**: Result provides guidance, not just description
- **Complete Integration**: All Stage 2 concepts meaningfully incorporated
- **Stakeholder Clarity**: Understandable to someone unfamiliar with CF14

### 4. **Iterative Refinement Process**

**Step 1: Identify Problem Pattern**
```bash
# Run same cell multiple times to check consistency
python3 -m chirality.cli compute-cell C --i 0 --j 0 --resolver openai --verbose
python3 -m chirality.cli compute-cell C --i 0 --j 0 --resolver openai --verbose
python3 -m chirality.cli compute-cell C --i 0 --j 0 --resolver openai --verbose
```

**Step 2: Modify Prompt Fragments**
Edit `chirality/core/cell_resolver.py::assemble_prompt()` methods:
- Adjust system context
- Refine operation instructions
- Enhance ontological context

**Step 3: Test and Compare**
```bash
# Test modified prompts
python3 -m chirality.cli compute-cell C --i 0 --j 0 --resolver openai --verbose --trace

# Compare trace files for quality improvements
```

**Step 4: Document Changes**
- Record what was changed and why
- Note impact on semantic quality
- Update this guide with new patterns

## Using Neo4j for Prompt Analysis

The working memory graph enables powerful analysis of prompt performance:

### Query Semantic Resolution Patterns
```cypher
// Find all Stage 2 semantic resolutions
MATCH (c:Cell)-[:HAS_STAGE]->(s:Stage:Semantic)
RETURN s.concepts, count(*) as frequency
ORDER BY frequency DESC
```

### Compare Prompt Versions
```cypher
// Find cells computed on different dates (different prompt versions)
MATCH (c:Cell {id: 'C-0-0'})-[:HAS_STAGE]->(s)
RETURN s, s.timestamp
ORDER BY s.timestamp
```

### Identify Resolution Quality Issues
```cypher
// Find very short or very long resolutions (potential quality issues)
MATCH (s:Stage:Semantic)
WHERE size(s.concepts[0]) < 10 OR size(s.concepts[0]) > 100
RETURN s.concepts, count(*) as frequency
```

## Advanced Prompt Patterns

### Context Window Optimization
- **Front-load critical context**: Place ontological coordinates early
- **Use semantic anchors**: Reference specific valley station and position
- **Minimize token waste**: Remove unnecessary explanations from system prompt

### Consistency Techniques
- **Establish semantic rules**: Clear definitions for multiplication vs addition
- **Use concrete examples**: "sufficient * reason = justification"  
- **Maintain voice consistency**: Same style and tone across operations

### Quality Control
- **JSON validation**: Ensure strict output format compliance
- **Term preservation**: Require exact echoing of input terms in `terms_used`
- **Warning system**: Use warnings for edge cases and missing inputs

## Prompt Evolution Strategy

### Version Control Approach
1. **Baseline**: Establish current prompt performance with test matrix
2. **Hypothesis**: Identify specific improvement target
3. **Implementation**: Modify specific prompt fragments
4. **Validation**: Test against same cells, compare quality
5. **Integration**: Deploy if improvements are consistent

### Measurement Approach
Since semantic quality is subjective, use multiple indicators:
- **Consistency**: Same inputs → similar outputs
- **Coherence**: Outputs make intuitive sense
- **Completeness**: All input concepts represented
- **Conciseness**: Appropriate length for purpose
- **Actionability**: Results provide useful guidance

## Getting Started with Refinement

### Immediate Next Steps
1. **Run baseline test matrix** across key cells with current prompts
2. **Document current output patterns** for comparison
3. **Identify one specific improvement target** (e.g., "reduce over-abstraction in Stage 2")
4. **Make targeted prompt modifications**
5. **Test and iterate**

### Tools for Manual Refinement
- **`--verbose` flag**: See stage-by-stage transformation
- **`--trace` flag**: Generate machine-readable logs
- **`--neo4j-export` flag**: Build corpus of results for analysis
- **Echo resolver**: Test pipeline mechanics without LLM variability

The prompt engineering process is where the semantic calculator evolves from functional to truly insightful. This manual refinement will establish the patterns for future automated optimization.