"""Environment-backed expense-agent configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

if os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"):
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "False")


@dataclass(frozen=True)
class ExpenseConfig:
    model: str = os.getenv("EXPENSE_MODEL", "gemini-3.1-flash-lite")
    review_threshold: float = float(os.getenv("EXPENSE_REVIEW_THRESHOLD", "100"))


config = ExpenseConfig()
