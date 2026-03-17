"""JSON-backed runtime config storage for dashboard overrides."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from app.config.settings import Settings
from app.models.runtime_config import RuntimeConfig


class RuntimeConfigStore:
    """Persist and restore runtime config overrides from local JSON file."""

    def __init__(self, *, path: str | Path, settings: Settings | None = None) -> None:
        self.path = Path(path)
        self.settings = settings or Settings()
        self.defaults = RuntimeConfig.from_settings(self.settings)

    def load(self) -> RuntimeConfig:
        """Load runtime config; fallback to defaults when file missing."""
        if not self.path.exists():
            return RuntimeConfig.model_validate(self.defaults.model_dump())

        raw_text = self.path.read_text(encoding="utf-8").strip()
        if not raw_text:
            return RuntimeConfig.model_validate(self.defaults.model_dump())

        try:
            payload = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            msg = f"Runtime config JSON is malformed: {exc.msg}"
            raise ValueError(msg) from exc

        if not isinstance(payload, dict):
            msg = "Runtime config payload must be a JSON object"
            raise ValueError(msg)

        merged = self.defaults.model_dump()
        merged.update(payload)
        try:
            return RuntimeConfig.model_validate(merged)
        except ValidationError as exc:
            msg = f"Runtime config payload is invalid: {exc.errors()}"
            raise ValueError(msg) from exc

    def save(self, config: RuntimeConfig) -> None:
        """Save runtime config object to disk."""
        try:
            validated = RuntimeConfig.model_validate(config.model_dump())
        except ValidationError as exc:
            msg = f"Cannot save invalid runtime config: {exc.errors()}"
            raise ValueError(msg) from exc

        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(validated.model_dump(mode="json"), indent=2),
            encoding="utf-8",
        )

    def reset_to_defaults(self) -> RuntimeConfig:
        """Reset stored runtime config to environment-backed defaults."""
        defaults = RuntimeConfig.model_validate(self.defaults.model_dump())
        self.save(defaults)
        return defaults
