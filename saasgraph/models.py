from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RiskLevel(str, Enum):
    NORMAL = "NORMAL"
    REVIEW = "REVIEW"
    HIGH_RISK = "HIGH_RISK"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class OAuthApp:
    app_id: str
    name: str
    publisher: str
    publisher_verified: bool
    admin_consent: bool
    scopes: tuple[str, ...]
    users: int
    token_persistent: bool
    dormant_days: int
    baseline_api_calls_per_hour: int
    observed_api_calls_per_hour: int
    resources: tuple[str, ...]
    external_tenant: bool
    expected_level: RiskLevel


@dataclass(frozen=True)
class Assessment:
    app_id: str
    name: str
    risk_level: RiskLevel
    risk_score: int
    scope_risk: int
    api_ratio: float
    users_exposed: int
    resources_reachable: int
    reasons: tuple[str, ...]
    recommended_actions: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "app_id": self.app_id,
            "name": self.name,
            "risk_level": self.risk_level.value,
            "risk_score": self.risk_score,
            "scope_risk": self.scope_risk,
            "api_ratio": self.api_ratio,
            "users_exposed": self.users_exposed,
            "resources_reachable": self.resources_reachable,
            "reasons": list(self.reasons),
            "recommended_actions": list(self.recommended_actions),
        }
