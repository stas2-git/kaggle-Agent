"""FastAPI adapter for the portfolio review service."""

from __future__ import annotations

import os
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from portfolio_agent.support.config import APPLICATION_NAME, load_config
from portfolio_agent.core.schemas import PortfolioReviewResult
from portfolio_agent.core.security import SecurityError
from portfolio_agent.service import review_portfolio


DEMO_DATASETS = {
    "loss_ratio_spike": "data/eval/loss_ratio_spike.csv",
    "clean_portfolio": "data/eval/clean_portfolio.csv",
    "premium_drop": "data/eval/premium_drop.csv",
    "benchmark_deterioration": "data/eval/benchmark_deterioration.csv",
}


class ReviewRequest(BaseModel):
    """Request body for an approved local/demo review."""

    dataset_ref: str = Field(
        ..., description="Approved demo alias or allowed local CSV path."
    )
    latest_month: str = Field(..., pattern=r"^\d{4}-\d{2}$")
    mode: Literal["online", "offline"] = "offline"
    model_name: str | None = None
    user_prompt: str | None = None


def _resolve_dataset_ref(dataset_ref: str) -> str:
    return DEMO_DATASETS.get(dataset_ref, dataset_ref)


app = FastAPI(
    title="Portfolio Agent",
    description="Local API adapter for the actuarial portfolio monitoring service.",
    version="0.1.0",
)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    """Return process liveness without touching model credentials."""

    return {"status": "ok", "application": APPLICATION_NAME}


@app.get("/readyz")
def readyz() -> dict[str, object]:
    """Return sanitized readiness/configuration details."""

    cfg = load_config(
        force_offline=os.environ.get("PORTFOLIO_AGENT_EXECUTION_MODE") == "offline"
    )
    return {
        "status": "ready",
        "application": cfg.application_name,
        "execution_mode": cfg.execution_mode,
        "model_configured": bool(cfg.model_name),
        "approved_dataset_aliases": sorted(DEMO_DATASETS),
    }


@app.post("/api/reviews", response_model=PortfolioReviewResult)
def create_review(request: ReviewRequest) -> PortfolioReviewResult:
    """Run a portfolio review through the shared service boundary."""

    input_path = _resolve_dataset_ref(request.dataset_ref)
    try:
        return review_portfolio(
            input_path=input_path,
            latest_month=request.latest_month,
            model_name=request.model_name,
            user_prompt=request.user_prompt,
            force_offline=request.mode == "offline",
        )
    except SecurityError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Dataset not found.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "portfolio_agent.fast_api_app:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8080")),
    )
