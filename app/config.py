from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class LocalConfig:
    """Local demo configuration."""

    SECRET_KEY: str = os.getenv("TANGRAM_SECRET_KEY", "dev-only-secret")
    DB_PATH: str = os.getenv("TANGRAM_DB_PATH", "data/duckdb/tangram_lab.duckdb")
    TRACE_PATH: str = os.getenv("TANGRAM_TRACE_PATH", "data/duckdb/traces.jsonl")
    PRIVACY_SALT: str = os.getenv("TANGRAM_PRIVACY_SALT", "dev-demo-salt")
    MLFLOW_TRACKING_URI: str = os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns")
