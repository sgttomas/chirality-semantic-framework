"""
Consolidated OpenAI interface for CF14 semantic operations.

This is the ONLY file in the codebase that imports OpenAI.
All semantic operations (multiplication, addition, interpretation) 
go through this centralized resolver with robust error handling,
retry logic, and JSON validation.
"""

import os
import json
import time
import hashlib
import unicodedata
import re
from typing import Dict, Any, List, Optional, Literal, Tuple
from datetime import datetime

try:
    from openai import OpenAI  # type: ignore
except Exception:
    OpenAI = None  # Defer hard failure until actually instantiated

from .types import Cell, Matrix
from .context import SemanticContext
from .prompts import SYSTEM_PROMPT


def normalize_text(s: str) -> str:
    """Normalize unicode and whitespace for consistent processing."""
    if s is None:
        return ""
    s = unicodedata.normalize("NFKC", str(s))
    s = re.sub(r"\s+", " ", s).strip()
    return s


def escape_for_prompt(s: str) -> str:
    """Escape string for safe embedding in prompts."""
    return json.dumps(normalize_text(s), ensure_ascii=False)[1:-1]


class CellResolver:
    """
    Consolidated OpenAI interface for all CF14 semantic operations.
    
    This is the centralized resolver that handles all LLM calls with:
    - Robust retry logic with exponential backoff
    - JSON validation and error handling  
    - Temperature control per operation type
    - Deterministic prompt hashing
    - Comprehensive error recovery
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o", seed: int = 42):
        if OpenAI is None:
            raise ImportError("OpenAI package required. Install with: pip install openai")

        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key required")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.seed = seed
        
        # Temperature settings for different operations (consolidated from ops.py)
        self.temperatures = {
            "multiply": 0.7,  # Creative intersection for semantic multiplication
            "add": 0.5,       # Tighter integration for semantic addition
            "interpret": 0.5, # Clear explanation for interpretation
            "*": 0.7,         # Alias for multiply
            "+": 0.5,         # Alias for add
            "⊙": 0.7          # Element-wise multiplication
        }
        
        # Retry configuration (from OpenAIResolver)
        self.max_retries = 3
        self.base_delay = 0.4
        
        # Default system frame for fragment composition (from prompts.py)
        self.default_system_frame = SYSTEM_PROMPT
    
    def assemble_prompt(self, valley_summary: str, station: str, row_label: str, col_label: str, 
                       operation_type: str, terms: Dict, operation_instructions: str = None) -> str:
        """
        Fragment composition - you control each piece.
        
        Dynamically assembles prompts from configurable fragments rather than static templates.
        This is the core of the fragment composition architecture.
        """
        fragments = []

        if valley_summary:
            fragments.append(f"Valley Context: {valley_summary}")

        fragments.append(f"Station: {station}")
        fragments.append(f"Coordinates: ({row_label}, {col_label})")

        if operation_instructions:
            fragments.append(f"Operation: {operation_instructions}")
        else:
            # Default operation instructions based on type
            if operation_type == "*":
                fragments.append("Operation: Semantic multiplication - fuse meanings at their intersection")
            elif operation_type == "interpret":
                fragments.append("Operation: Ontological lensing - interpret through row/column context")
            elif operation_type == "synthesize":
                fragments.append("Operation: Synthesis - apply canonical D formula")

        fragments.append(f"Terms: {terms}")

        return "\n\n".join(fragments)

    def resolve_semantic_pair(self, pair: str, context: SemanticContext) -> str:
        """
        Stage 2: Use fragment composition for semantic multiplication.
        
        Takes a word pair like 'Values * Necessary' and resolves it to a concept
        like 'Essential Values' using the full SemanticContext for guidance.
        """
        system_prompt = context.system_frame or self.default_system_frame

        user_prompt = self.assemble_prompt(
            valley_summary=context.valley_summary,
            station=context.station_context,
            row_label=context.row_label,
            col_label=context.col_label,
            operation_type="*",
            terms={"term_a": pair.split(" * ")[0], "term_b": pair.split(" * ")[1]},
            operation_instructions=context.operation_instructions
        )

        response, metadata = self._call_openai(system_prompt, user_prompt, "multiply")
        return response.get("text", "")

    def apply_ontological_lens(self, content: str, context: SemanticContext) -> str:
        """
        Stage 3: Fragment-based ontological lensing.
        
        Interprets content through the ontological lenses of the row/column coordinates.
        This is where deep, context-specific insights are generated.
        """
        system_prompt = context.system_frame or self.default_system_frame

        user_prompt = self.assemble_prompt(
            valley_summary=context.valley_summary,
            station=context.station_context,
            row_label=context.row_label,
            col_label=context.col_label,
            operation_type="interpret",
            terms={"content": content},
            operation_instructions=context.operation_instructions
        )

        response, metadata = self._call_openai(system_prompt, user_prompt, "interpret")
        return response.get("text", "")
    
# _get_system_prompt() method removed - now using imported SYSTEM_PROMPT from prompts.py

# Old methods removed - replaced by fragment composition architecture

# Old add_terms() and interpret_term() methods removed - replaced by fragment composition

    def _call_openai(self, system_prompt: str, user_prompt: str, operation: str = "semantic") -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Consolidated OpenAI call with robust error handling.
        
        Combines the best patterns from ops.py OpenAIResolver:
        - Exponential backoff retry logic
        - JSON extraction and validation
        - Prompt hashing for audit trails
        - Comprehensive error recovery
        
        Returns:
            Tuple of (parsed_response, metadata)
        """
        temperature = self.temperatures.get(operation, 0.5)
        prompt_hash_val = self._prompt_hash(system_prompt, user_prompt)
        
        attempt = 0
        last_err: Optional[Exception] = None
        t0 = time.time()

        while attempt <= self.max_retries:
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    temperature=temperature,
                    top_p=0,
                    seed=self.seed,
                    max_tokens=200,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                
                # Extract and validate JSON content
                raw = resp.choices[0].message.content or ""
                js = self._extract_json(raw)
                obj = json.loads(js)
                self._validate_obj(obj)
                
                # Calculate metadata (consolidated from ops.py)
                dt = int((time.time() - t0) * 1000)
                meta = {
                    "modelId": resp.model,
                    "latencyMs": dt,
                    "promptHash": prompt_hash_val,
                    "systemVersion": self._system_version_hash(),
                    "rawLen": len(raw),
                    "attempts": attempt + 1,
                    "temperature": temperature,
                    "maxTokens": 200,
                    "createdAt": self._now_iso(),
                    "phase": operation,
                }
                
                return obj, meta
                
            except Exception as e:
                last_err = e
                if attempt >= self.max_retries:
                    break
                    
                # Exponential backoff (from ops.py)
                wait_time = self.base_delay * (2 ** attempt)
                time.sleep(wait_time)
                attempt += 1

        # All retries exhausted - return error response
        error_response = {
            "text": f"ERROR: Failed to process {operation}",
            "terms_used": [],
            "warnings": [f"openai_failure: {last_err}"]
        }
        error_meta = {
            "modelId": self.model,
            "latencyMs": 0,
            "promptHash": prompt_hash_val,
            "error": str(last_err),
            "operation": operation,
            "createdAt": self._now_iso(),
            "attempts": attempt + 1,
            "phase": "error"
        }
        return error_response, error_meta
    
    # Consolidated helper methods from ops.py OpenAIResolver
    
    def _prompt_hash(self, system: str, user: str) -> str:
        """Generate deterministic hash for system + user prompt combination."""
        h = hashlib.sha256()
        h.update(normalize_text(system).encode("utf-8"))
        h.update(b"\n\n")
        h.update(normalize_text(user).encode("utf-8"))
        return h.hexdigest()

    def _system_version_hash(self) -> str:
        """Hash of current system prompt for versioning."""
        return hashlib.sha256(normalize_text(SYSTEM_PROMPT).encode("utf-8")).hexdigest()

    def _now_iso(self) -> str:
        """Generate ISO-8601 timestamp for graph compatibility."""
        return datetime.utcnow().isoformat(timespec="seconds") + "Z"

    def _extract_json(self, text: str) -> str:
        """Extract JSON object from model output, handling stray prose."""
        if not text:
            raise ValueError("Empty model output")
        
        # Find the first '{' and last '}' to guard against stray prose
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("No JSON object found in model output")
        
        return text[start:end+1]

    def _validate_obj(self, obj: Dict[str, Any]) -> None:
        """Validate that object conforms to expected CF14 schema."""
        if not isinstance(obj, dict):
            raise ValueError("Output must be a JSON object")
        
        # Check required keys
        if "text" not in obj or "terms_used" not in obj or "warnings" not in obj:
            raise ValueError("Missing required keys (text, terms_used, warnings)")
        
        # Type validation
        if not isinstance(obj["text"], str):
            raise ValueError("'text' must be string")
        
        if not (isinstance(obj["terms_used"], list) and all(isinstance(t, str) for t in obj["terms_used"])):
            raise ValueError("'terms_used' must be list[str]")
        
        if not (isinstance(obj["warnings"], list) and all(isinstance(w, str) for w in obj["warnings"])):
            raise ValueError("'warnings' must be list[str]")