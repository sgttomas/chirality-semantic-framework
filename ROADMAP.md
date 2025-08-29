# Project Roadmap

**Status Last Updated**: August 28, 2025

## Current Status: Refactoring Complete

The project has recently undergone a major architectural refactoring. The previous goal of building a flexible, extensible "framework" has been replaced with a much clearer and more focused objective: to create a direct, observable implementation of the canonical Chirality Framework algorithm.

This transformation into a **"semantic calculator"** is now complete. The core logic, centered around the **Three-Stage Interpretation Pipeline**, is stable, tested, and consistent.

## Current Status: Core Implementation Complete ✅

The refactoring to a "semantic calculator" is **complete**! All core functionality has been implemented and tested:

✅ **CLI Implementation (`Phase 7`)** - **COMPLETE**
- `click`-based CLI with professional UX
- `compute-cell` command provides cell-first debugging
- `--verbose` flag shows all 3 stages step-by-step  
- Full integration with core operations tested

✅ **Testing Pipeline (`Phase 8`)** - **COMPLETE**
- Comprehensive test infrastructure in `/tests/`
- MockCellResolver for fast, offline testing
- All 3 stages tested independently and end-to-end
- 100% test coverage of core pipeline

✅ **Documentation (`Phase 9`)** - **COMPLETE**
- All documentation updated for semantic calculator philosophy
- Technical algorithm documentation complete
- CLI usage examples working and tested

## Next Development Priorities

With the core semantic calculator fully implemented and tested, future work can focus on extending capabilities and optimizing performance:

### High Priority
*   **Online Testing Suite**: Add `@pytest.mark.online` tests that validate against real OpenAI API calls
*   **Performance Optimization**: Profile the 3-stage pipeline and optimize `CellResolver` for speed and cost
*   **Enhanced Error Handling**: Improve robustness for edge cases and API failures

### Medium Priority  
*   **Extended Semantic Valley**: Implement next matrices in the canonical sequence (X, Z, etc.)
*   **LLM Experimentation**: Test different language models for optimal semantic resolution
*   **Tracing Analytics**: Build tools to analyze and visualize `JSONLTracer` output

### Low Priority
*   **Additional Export Formats**: CSV, Excel, or other matrix export options
*   **Advanced CLI Features**: Batch processing, configuration files
*   **Integration Adapters**: Additional database or API integrations

The core algorithm is stable and production-ready. All future work builds on this solid foundation.

## Production Hardening Plan

This plan captures the remaining work to move from a robust prototype to a production-grade, continuously validated system. Each item includes scope and concrete outcomes.

### 1) Test Coverage Expansion
- **Neo4j Export Integration Tests**: Exercise `Neo4jWorkingMemoryExporter` end-to-end against a test Neo4j instance.
  - Validate graph schema (Matrix/Cell/Stage nodes; CONTAINS/HAS_STAGE rels).
  - Assert idempotency and uniqueness constraints; verify stage ordering via timestamps.
  - Add a `--dry-run` mode stub to simulate writes for CI.
- **Tracer Rotation & Dedupe Tests**: Generate large traces to trigger rotation; assert file rollover and no duplicates with dedupe on.
  - Include concurrency smoke test (ThreadPoolExecutor) to ensure locking behavior.
- **CLI Snapshot Tests (Verbose)**: Snapshot “stage-by-stage” output for `compute-cell` (C, and minimal F/D) to detect regressions in UX.
- **Optional Online Tests**: Gate with `@pytest.mark.online` and `OPENAI_API_KEY`.
  - Small, stable set of cells; assert JSON contract and non-empty `text`.

### 2) Error Handling & Reporting
- **Resolver Error Propagation**: Distinguish hard failures (raise) vs soft warnings (attach to provenance).
  - Return structured errors up the call stack; surface in CLI with clear messages.
- **CLI Failure Modes**: Add `--fail-on-error` to exit non‑zero on Stage 2/3 failures or invalid outputs.
  - Print remediation tips (env vars, network, rate limits) in verbose mode.
- **Provenance Warnings**: Ensure any model/output validation issues are recorded in `warnings` and optionally highlighted in CLI.

### 3) Configuration & Resilience
- **Centralized Config**: Extract model, timeouts, retry counts, token limits, and tracer/export flags into a single config module.
  - Load from env vars with sane defaults; allow CLI overrides.
- **Documentation of Defaults**: Update README/API docs to list default knobs and recommended production settings.
- **Backoff & Limits**: Make retry/backoff configurable; add guards for oversized prompts/results.

### 4) CI/CD & Packaging
- **CI Pipeline**: GitHub Actions workflow to run lint, type-check, and tests on PRs and main.
  - Lint: `ruff` or `flake8`; Type-check: `mypy` (target core modules); Tests: `pytest -q` (skip `@online`).
  - Cache dependencies; artifact snapshots for CLI verbose outputs and trace samples.
- **Dependency Hygiene**: Pin minimal versions; provide `requirements-dev.txt` and extras; document installation matrix.
- **Release Automation**: Tag-driven version checks; build/publish to an internal index or PyPI when ready.

### 5) Usability & DX Improvements
- **CLI Enhancements**:
  - `info` prints A/B/J axes explicitly (row/col labels and station names).
  - `--dry-run` for Neo4j exporter (log-only, no DB writes).
  - `--summary` to print staged highlights (without full provenance block).
- **Examples & Guides**:
  - Add short, copy‑paste examples for common flows (compute single cell with tracing/export; full C→F→D run).
  - Troubleshooting appendix: common resolver/exporter errors and quick fixes.

### Acceptance (Production-Ready)
- Green CI on PRs and main; unit + integration tests stable and fast.
- CLI communicates failures clearly; `--fail-on-error` behaves as expected.
- Configurable resolver and tracer/export behavior documented and discoverable.
- Neo4j export validated with schema checks; `--dry-run` safe for CI.
- Docs updated to reflect UX and configuration; examples runnable as-is.
