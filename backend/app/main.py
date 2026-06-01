"""FastAPI application entrypoint."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from .config import settings
from .api import characters, generate, versions, traces, export, share
from .rate_limit import limiter

app = FastAPI(title="Re:Roll Character Builder API", version="1.0.0")

# Rate limiting (per-user daily cap on generation).
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(characters.router)
app.include_router(generate.router)
app.include_router(versions.router)
app.include_router(traces.router)
app.include_router(export.router)
app.include_router(share.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
