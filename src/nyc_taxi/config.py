"""Shared analytical windows and checkpoint identity."""
from dataclasses import asdict, dataclass
import hashlib
import json

PROCESSING_VERSION = "2.0"


@dataclass(frozen=True)
class AnalysisConfig:
    max_duration_min: float = 120
    max_distance_mi: float = 60
    max_speed_mph: float = 60
    monetary_alert_usd: float = 500

    def __post_init__(self):
        import math
        if any(not math.isfinite(v) or v <= 0 for v in asdict(self).values()):
            raise ValueError("Analytical thresholds must be finite and positive")

    @property
    def fingerprint(self) -> str:
        payload = {"version": PROCESSING_VERSION, **asdict(self)}
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


DEFAULT_CONFIG = AnalysisConfig()
