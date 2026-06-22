"""Local FastAPI server with ADK Pub/Sub trigger endpoints."""

from __future__ import annotations

import json
import logging
import os

import uvicorn
from google.adk.cli.fast_api import get_fast_api_app
from starlette.requests import Request

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

AGENTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = get_fast_api_app(
    agents_dir=AGENTS_DIR,
    web=True,
    trigger_sources=["pubsub"],
    otel_to_cloud=False,
)
app.title = "Ambient Expense Agent"


@app.middleware("http")
async def normalize_pubsub_subscription(request: Request, call_next):  # type: ignore[no-untyped-def]
    """Use the short Pub/Sub subscription name as the ADK user ID."""
    if request.method == "POST" and request.url.path.endswith("/trigger/pubsub"):
        body = await request.body()
        try:
            envelope = json.loads(body)
            subscription = str(envelope.get("subscription", ""))
            if "/" in subscription:
                envelope["subscription"] = subscription.rsplit("/", 1)[-1]
                request._body = json.dumps(envelope).encode("utf-8")
        except (json.JSONDecodeError, TypeError):
            logger.warning("Received an invalid Pub/Sub JSON envelope")
    return await call_next(request)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
