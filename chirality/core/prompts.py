# chirality_prompts.py
"""
Prompt templates and canonical system message for the Chirality Framework Phase-1 build.

The core metaphor: Wayfinding through an unknown semantic valley.
Each station is a landmark in this valley.
Each matrix cell is a coordinate (row_label × col_label) inside that landmark.
Your job as the LLM: preserve and integrate meaning while mapping it faithfully into the valley's meta-ontology.
"""

import re
import unicodedata
import json

def q(s: str) -> str:
    """Normalize unicode, collapse whitespace, and escape for prompt embedding."""
    if s is None:
        return ""
    # Normalize unicode to NFKC (e.g., curly quotes → straight)
    s = unicodedata.normalize("NFKC", str(s))
    # Collapse internal whitespace while preserving single spaces
    s = re.sub(r"\s+", " ", s).strip()
    # Escape for embedding between quotes in our prompts
    # Use json.dumps then strip outer quotes for robust escaping
    return json.dumps(s, ensure_ascii=False)[1:-1]

def _ensure_valley_summary(valley_summary: str) -> str:
    return valley_summary.strip() or "Semantic Valley: Problem Statement → Requirements → Objectives → Solution Objectives"

# Canonical system prompt — used for all semantic operations
SYSTEM_PROMPT = """\
You are the semantic engine for the Chirality Framework (Phase-1 canonical build).

The Chirality Framework is a meta-operating system for meaning. It frames knowledge work as wayfinding through an unknown semantic valley:
- The valley is the conceptual space for this domain.
- Stations are landmarks (each has a distinct role in meaning transformation).
- Rows and columns are fixed ontological axes; preserve them at all times.
- A cell is a coordinate: (row_label × col_label) at a given station.

Mission:
- Operate ONLY within the provided valley + station context.
- Apply exactly ONE semantic operation per call: multiplication (×), addition (+), or interpretation (separate lens).
- Preserve the identity of source terms; integrate them, do not overwrite them.
- Resolve ambiguity inside the operation; do not delete it.
- Keep every output traceable to its sources.

Voice & style (vibe):
- Confident, concrete, humane; no fluff or marketing language.
- Prefer strong verbs and specific nouns over abstractions.
- Avoid hedging ("might", "could") unless uncertainty is essential and then state it plainly.
- Length: × and + = 1–2 sentences. Interpretation ≤ 2 sentences, stakeholder-friendly, ontology-preserving.

Output contract (STRICT):
- Return ONLY a single JSON object with keys: "text", "terms_used", "warnings".
- "terms_used" must echo the exact provided source strings (after normalization) that you actually integrated.
- If any required input is missing/empty, include a warning like "missing_input:<name>".
- Do NOT include code fences, prose, or any text outside the JSON object.
"""

def generate_valley_summary(valley: dict | None, station: dict | None) -> str:
    """
    Build a compact 'valley map' like:
      Semantic Valley: Problem Statement → [Requirements] → Objectives → Solution Objectives
    The current station is bracketed.
    Expects GraphQL shapes:
      valley = { "stations": [ { "name": str, "index": int }, ... ] }
      station = { "index": int, "name": str }
    """
    if not valley or not isinstance(valley, dict):
        return "Semantic Valley: Problem Statement → Requirements → Objectives → Solution Objectives"
    stations = valley.get("stations") or []
    names = []
    for i, s in enumerate(stations):
        names.append(s.get("name", f"Station {i}"))
    if not names:
        names = ["Problem Statement", "Requirements", "Objectives", "Solution Objectives"]
    cur = (station or {}).get("index", None)
    if isinstance(cur, int) and 0 <= cur < len(names):
        names[cur] = f"[{names[cur]}]"
    return f"Semantic Valley: {' → '.join(names)}"

# === Static templates removed ===
# All prompt composition now happens dynamically in CellResolver.assemble_prompt()
# This follows the fragment composition architecture where prompts are built
# from configurable fragments rather than fixed templates.

# The q() function and valley utilities remain available for fragment composition