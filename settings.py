"""Shared policy and budgets. Never derive access grants from a question/widget."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import os
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env", override=False)


@dataclass(frozen=True)
class QueryOptions:
    project: str = "All"
    corpus: str = "All"
    # Server-supplied only. The public demo has no login and grants no private scope.
    grants: frozenset[str] = field(default_factory=frozenset)
    unavailable: frozenset[str] = field(default_factory=frozenset)
    max_hops: int = 3
    max_nodes: int = 36
    top_k: int = 8
    max_context_words: int = 1400
    now: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    use_model: bool = False

    def __post_init__(self):
        if not 1 <= self.max_hops <= 3 or not 1 <= self.max_nodes <= 64:
            raise ValueError("Graph budget out of range")
        if not 1 <= self.top_k <= 12 or not 100 <= self.max_context_words <= 2400:
            raise ValueError("Context budget out of range")
        if self.corpus not in {"All", "Synthetic", "Supplied"}:
            raise ValueError("Unknown corpus filter")


def index_path():
    return Path(os.getenv("QEI_CORPUS_PATH") or str(ROOT / "data/index.json"))


def freshness(doc, now):
    value = doc.get("updated_at")
    if not value:
        return "unknown"
    date = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if date.tzinfo is None:
        date = date.replace(tzinfo=timezone.utc)  # Date-only public notes use UTC day precision.
    age = (now - date).total_seconds() / 86400
    limit = 7 if doc["source_type"] == "testops" else 180 if doc["document_type"] == "product_documentation" else 30
    return "future-dated" if age < 0 else "current" if age <= limit else "stale"
