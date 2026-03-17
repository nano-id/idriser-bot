"""Logging helpers."""

from __future__ import annotations

import logging
from pathlib import Path


def setup_logging(*, output_dir: str, run_id: str, log_level: str, log_prefix: str = "signal_engine") -> Path:
    """Configure console and file logging for a scan run."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    log_path = Path(output_dir) / f"{log_prefix}_{run_id}.log"

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Replace existing handlers to avoid duplicate output on repeated runs.
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)
    return log_path
