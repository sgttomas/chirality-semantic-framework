"""
Production-ready JSONL tracer for semantic journey tracking in Chirality Framework.

Provides append-only, thread-safe, rotation-capable tracing of all semantic operations
with deterministic hashing for deduplication and full context preservation.
"""

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict, field
from collections import deque
import threading
import uuid
import logging

logger = logging.getLogger(__name__)


@dataclass
class TraceEvent:
    """Complete semantic event record for audit trail."""
    
    # Core identity
    stage: str  # "product:k=0", "sum", "interpret", "final"
    matrix: str
    i: int
    j: int
    row_label: str
    col_label: str
    
    # Semantic content
    text: str
    terms_used: List[str]
    warnings: List[str]
    products: Optional[List[str]] = None  # For construct stages
    
    # Context
    thread_id: str = ""
    run_id: str = ""
    station: str = ""
    valley_summary: str = ""
    
    # Operation details
    pattern: str = ""
    stage_plan: List[str] = field(default_factory=list)
    inputs: Dict[str, Any] = field(default_factory=dict)
    
    # Technical metadata
    model_id: str = ""
    latency_ms: int = 0
    prompt_hash: str = ""
    event_hash: str = ""
    timestamp: str = ""
    
    # Schema versioning
    v: int = 1


class JSONLTracer:
    """
    Production-ready semantic journey tracer with FIFO deduplication and rotation.
    
    Features:
    - Append-only JSONL format for resilience and streaming
    - Thread-safe operations with proper locking
    - Automatic file rotation at size threshold
    - FIFO deduplication with bounded memory usage
    - Deterministic content hashing for reproducibility
    - Error resilience - continues on I/O errors
    
    Usage:
        with JSONLTracer() as tracer:
            tracer.trace_stage("product:k=0", cell_context, result, extras)
    """
    
    # Standardized stage names
    STAGE_PRODUCT = "product:k={k}"
    STAGE_SUM = "sum"
    STAGE_INTERPRET = "interpret"
    STAGE_FINAL = "final"
    
    def __init__(self, 
                 base_path: Path = Path("traces"),
                 thread_id: str = None,
                 dedupe: bool = True,
                 max_bytes: int = 50 * 1024 * 1024,  # 50MB rotation
                 max_seen: int = 100_000):  # Memory cap for dedupe
        """
        Initialize the tracer.
        
        Args:
            base_path: Root directory for trace files
            thread_id: Unique identifier for this trace session
            dedupe: Whether to deduplicate events by content hash
            max_bytes: Maximum file size before rotation
            max_seen: Maximum deduplication cache size
        """
        self.thread_id = thread_id or self._generate_thread_id()
        self.run_id = self._generate_run_id()
        self.base_path = base_path
        self.dedupe = dedupe
        self.max_bytes = max_bytes
        self.max_seen = max_seen
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Correct FIFO dedupe with deque + set
        if dedupe:
            self.seen_order = deque()  # Maintains insertion order
            self.seen_set = set()      # Fast membership check
        else:
            self.seen_order = None
            self.seen_set = None
            
        self._file_handles = {}
        self._file_paths = {}  # For diagnostics
        
    def _generate_thread_id(self) -> str:
        """Generate sanitized thread ID."""
        tid = f"{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
        return self._sanitize_path(tid)
    
    def _generate_run_id(self) -> str:
        """Generate unique run ID."""
        return uuid.uuid4().hex[:12]
    
    def trace_stage(self, 
                    stage_type: str, 
                    cell_context,  # CellContext type
                    result,        # SemanticResult type
                    extras: Dict[str, Any] = None) -> None:
        """
        Trace a semantic stage event.
        
        Args:
            stage_type: Type of stage (e.g., "product:k=0", "sum", "interpret", "final")
            cell_context: Context object with matrix, i, j, labels, pattern, inputs
            result: Semantic result with text, terms_used, warnings, metadata
            extras: Optional additional context (station, valley_summary, products, etc.)
        """
        with self._lock:
            try:
                # Build event
                event = self._build_event(stage_type, cell_context, result, extras)
                
                # Dedupe with correct FIFO
                if self.dedupe:
                    if event.event_hash in self.seen_set:
                        return  # Skip duplicate
                    
                    # Add to both structures
                    self.seen_order.append(event.event_hash)
                    self.seen_set.add(event.event_hash)
                    
                    # Evict oldest if over limit
                    if len(self.seen_set) > self.max_seen:
                        oldest = self.seen_order.popleft()
                        self.seen_set.remove(oldest)
                
                # Get file handle
                file_handle = self._get_file_handle(cell_context.matrix)
                
                # Serialize to JSON
                json_line = json.dumps(
                    asdict(event),
                    sort_keys=True,
                    separators=(',', ':'),
                    ensure_ascii=False
                )
                
                # Write with correct byte tracking
                line_with_newline = json_line + '\n'
                bytes_to_write = line_with_newline.encode('utf-8')
                
                file_handle.write(line_with_newline)
                file_handle.flush()
                
                # Check rotation based on actual file size
                self._check_rotation_needed(cell_context.matrix)
                
            except Exception as e:
                # Log error but don't block semantic operations
                logger.warning(f"Tracer error (continuing): {e}")
    
    def _build_event(self, stage_type: str, cell_context, result, extras: Dict[str, Any]) -> TraceEvent:
        """Build complete trace event with deterministic hashing."""
        extras = extras or {}
        
        # Content for hashing (includes row/col labels and products)
        content_for_hash = {
            "matrix": cell_context.matrix,
            "i": cell_context.i,
            "j": cell_context.j,
            "stage": stage_type,
            "row_label": cell_context.row_label,
            "col_label": cell_context.col_label,
            "text": result.text,
            "terms_used": sorted(result.terms_used),
            "warnings": sorted(result.warnings),
            "prompt_hash": extras.get("prompt_hash", "")
        }
        
        # Include products in hash for construct stages
        if "products" in extras and extras["products"]:
            content_for_hash["products"] = sorted(extras["products"])
        
        event_hash = self._compute_hash(content_for_hash)
        
        return TraceEvent(
            stage=stage_type,
            matrix=cell_context.matrix,
            i=cell_context.i,
            j=cell_context.j,
            row_label=cell_context.row_label,
            col_label=cell_context.col_label,
            text=result.text,
            terms_used=result.terms_used,
            warnings=result.warnings or [],
            products=extras.get("products"),
            thread_id=self.thread_id,
            run_id=self.run_id,
            station=extras.get("station", ""),
            valley_summary=extras.get("valley_summary", ""),
            pattern=getattr(cell_context, 'pattern', ''),
            stage_plan=extras.get("stage_plan", []),
            inputs=getattr(cell_context, 'inputs', {}),
            model_id=result.metadata.get("model_id", "") if hasattr(result, 'metadata') else "",
            latency_ms=result.metadata.get("latency_ms", 0) if hasattr(result, 'metadata') else 0,
            prompt_hash=extras.get("prompt_hash", ""),
            event_hash=event_hash,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    
    def _compute_hash(self, content: Dict) -> str:
        """Compute canonical hash for deduplication."""
        canonical = json.dumps(content, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical.encode('utf-8')).hexdigest()[:16]
    
    def _get_file_handle(self, matrix: str):
        """Get or create file handle with size-based rotation."""
        if matrix not in self._file_handles:
            self._open_new_file(matrix)
        return self._file_handles[matrix]
    
    def _check_rotation_needed(self, matrix: str):
        """Check if rotation needed based on actual file size."""
        if matrix in self._file_paths:
            file_path = self._file_paths[matrix]
            try:
                if file_path.stat().st_size > self.max_bytes:
                    self._file_handles[matrix].close()
                    del self._file_handles[matrix]
                    del self._file_paths[matrix]
                    self._open_new_file(matrix)
            except:
                pass  # File might not exist yet
    
    def _open_new_file(self, matrix: str):
        """Open new file with rotation counter."""
        dir_path = self.base_path / self._sanitize_path(self.thread_id)
        dir_path.mkdir(parents=True, exist_ok=True)
        
        base_name = f"{matrix}-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
        file_path = self._find_available_path(dir_path, base_name)
        
        self._file_handles[matrix] = open(file_path, 'a', buffering=1, encoding='utf-8')
        self._file_paths[matrix] = file_path
    
    def _find_available_path(self, dir_path: Path, base_name: str) -> Path:
        """Find available file path with rotation counter."""
        file_path = dir_path / f"{base_name}.jsonl"
        counter = 1
        while file_path.exists():
            file_path = dir_path / f"{base_name}-{counter}.jsonl"
            counter += 1
        return file_path
    
    def _sanitize_path(self, name: str) -> str:
        """Sanitize string for filesystem safety."""
        return "".join(c if c.isalnum() or c in '-_' else '_' for c in name)
    
    def get_current_path(self, matrix: str) -> Optional[Path]:
        """
        Get current file path for diagnostics.
        
        Args:
            matrix: Matrix name to get path for
            
        Returns:
            Current file path or None if not open
        """
        return self._file_paths.get(matrix)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup."""
        self.close()
    
    def close(self):
        """Close all file handles safely."""
        with self._lock:
            for handle in self._file_handles.values():
                try:
                    handle.close()
                except:
                    pass
            self._file_handles.clear()
            self._file_paths.clear()