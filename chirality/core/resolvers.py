"""
Clean resolvers for CF14 semantic calculator.

Contains only the essential EchoResolver for testing purposes.
All production semantic resolution goes through the CellResolver.
"""

from typing import List, Dict, Any, Literal, Callable
from .types import Matrix


class EchoResolver:
    """
    Deterministic, zero-LLM resolver for testing.
    
    Returns predictable outputs based on operation type and matrix names.
    Perfect for testing the 3-stage pipeline without LLM calls.
    """
    
    def resolve(self, op: Literal["*", "+", "×", "interpret", "⊙"], 
                inputs: List[Matrix], system_prompt: str, user_prompt: str, 
                context: Dict[str, Any]) -> List[List[str]]:
        """Return deterministic 2D array based on operation type."""
        rows: int = 0
        cols: int = 0
        def _uninit(_r: int, _c: int) -> str:
            raise RuntimeError("uninitialized op")
        val: Callable[[int, int], str] = _uninit

        if op == "*":
            A, B = inputs
            rows, cols = A.shape[0], B.shape[1]
            def _val(r: int, c: int) -> str:
                return f"*:{A.name}[{r},:]{B.name}[:,{c}]"
            val = _val
        elif op == "+":
            A, F = inputs
            rows, cols = A.shape
            def _val(r: int, c: int) -> str:
                return f"+:{A.name}[{r},{c}]⊕{F.name}[{r},{c}]"
            val = _val
        elif op == "interpret":
            (B,) = inputs
            rows, cols = B.shape
            def _val(r: int, c: int) -> str:
                return f"interp:{B.name}[{r},{c}]"
            val = _val
        elif op == "⊙":
            J, C = inputs
            rows, cols = J.shape
            def _val(r: int, c: int) -> str:
                return f"⊙:{J.name}[{r},{c}]×{C.name}[{r},{c}]"
            val = _val
        elif op == "×":
            A, B = inputs
            rows = A.shape[0] * B.shape[0]
            cols = A.shape[1] * B.shape[1]
            def _val(r: int, c: int) -> str:
                ar, ac = r // B.shape[0], c // B.shape[1]
                br, bc = r % B.shape[0], c % B.shape[1]
                return f"×:{A.name}[{ar},{ac}]⨂{B.name}[{br},{bc}]"
            val = _val
        else:
            raise ValueError(f"Unknown op: {op}")

        return [[val(r, c) for c in range(cols)] for r in range(rows)]