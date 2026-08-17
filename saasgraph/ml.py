from __future__ import annotations

import math
import random
from dataclasses import asdict, dataclass

import numpy as np
from sklearn.ensemble import IsolationForest

from .engine import SCOPE_WEIGHTS, assess
from .models import OAuthApp

MODEL_NAME = "IsolationForest"
RANDOM_STATE = 43
REFERENCE_SAMPLES = 800
FEATURE_NAMES = (
    "scope_risk",
    "scope_count",
    "sensitive_scope_count",
    "log_users",
    "persistent_token",
    "log_dormant_days",
    "log_api_ratio",
    "resource_count",
    "publisher_unverified",
    "admin_consent",
    "external_tenant",
)


@dataclass(frozen=True)
class SaaSMLFinding:
    app_id: str
    name: str
    rule_score: int
    anomaly_percentile: float
    ml_outlier: bool
    hybrid_priority: int
    top_deviations: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def feature_vector(app: OAuthApp) -> np.ndarray:
    scope_risk = min(30, sum(SCOPE_WEIGHTS.get(scope, 5) for scope in app.scopes))
    sensitive = sum(SCOPE_WEIGHTS.get(scope, 5) >= 8 for scope in app.scopes)
    ratio = app.observed_api_calls_per_hour / max(1, app.baseline_api_calls_per_hour)
    return np.asarray(
        [
            scope_risk,
            len(app.scopes),
            sensitive,
            math.log1p(app.users),
            int(app.token_persistent),
            math.log1p(app.dormant_days),
            math.log1p(ratio),
            len(app.resources),
            int(not app.publisher_verified),
            int(app.admin_consent),
            int(app.external_tenant),
        ],
        dtype=float,
    )


def _normal_reference(seed: int = RANDOM_STATE, samples: int = REFERENCE_SAMPLES) -> np.ndarray:
    rng = random.Random(seed)
    rows = []
    for _ in range(samples):
        scope_count = rng.choice([1, 1, 1, 2, 2, 3])
        scope_risk = max(2, min(22, round(rng.gauss(7 + 3 * (scope_count - 1), 3))))
        sensitive = 0 if scope_risk < 8 else rng.choice([0, 0, 1])
        users = max(1, round(math.exp(rng.gauss(3.0, 0.8))))
        persistent = int(rng.random() < 0.32)
        dormant = max(0, round(rng.gauss(12, 18)))
        api_ratio = max(0.25, rng.lognormvariate(0.0, 0.35))
        resources = rng.choice([1, 1, 2, 2, 3])
        unverified = int(rng.random() < 0.08)
        admin = int(rng.random() < 0.20)
        external = int(rng.random() < 0.12)
        rows.append(
            [
                scope_risk,
                scope_count,
                sensitive,
                math.log1p(users),
                persistent,
                math.log1p(dormant),
                math.log1p(api_ratio),
                resources,
                unverified,
                admin,
                external,
            ]
        )
    return np.asarray(rows, dtype=float)


def analyze_apps(apps: tuple[OAuthApp, ...] | list[OAuthApp]) -> list[SaaSMLFinding]:
    inventory = list(apps)
    if not inventory:
        return []

    reference = _normal_reference()
    matrix = np.vstack([feature_vector(app) for app in inventory])
    model = IsolationForest(
        n_estimators=180,
        contamination=0.06,
        random_state=RANDOM_STATE,
    )
    model.fit(reference)

    ref_scores = -model.score_samples(reference)
    scores = -model.score_samples(matrix)
    predictions = model.predict(matrix)
    mean = reference.mean(axis=0)
    std = np.where(reference.std(axis=0) < 1e-6, 1.0, reference.std(axis=0))

    findings = []
    for i, app in enumerate(inventory):
        percentile = round(float(100.0 * np.mean(ref_scores <= scores[i])), 1)
        z = (matrix[i] - mean) / std
        top = np.argsort(np.abs(z))[::-1][:3]
        deviations = tuple(FEATURE_NAMES[int(index)] for index in top if abs(z[int(index)]) >= 1.0)
        rule_score = assess(app).risk_score
        adjustment = round(max(0.0, percentile - 80.0) / 20.0 * 12)
        hybrid = min(100, rule_score + adjustment)
        findings.append(
            SaaSMLFinding(
                app_id=app.app_id,
                name=app.name,
                rule_score=rule_score,
                anomaly_percentile=percentile,
                ml_outlier=bool(predictions[i] == -1),
                hybrid_priority=hybrid,
                top_deviations=deviations,
            )
        )

    return sorted(findings, key=lambda row: (row.hybrid_priority, row.anomaly_percentile, row.app_id), reverse=True)


def ml_summary(apps: tuple[OAuthApp, ...] | list[OAuthApp]) -> dict[str, object]:
    findings = analyze_apps(apps)
    return {
        "model": MODEL_NAME,
        "normal_reference_samples": REFERENCE_SAMPLES,
        "features": list(FEATURE_NAMES),
        "outliers": sum(row.ml_outlier for row in findings),
        "mean_anomaly_percentile": round(sum(row.anomaly_percentile for row in findings) / len(findings), 1) if findings else 0.0,
        "meaning": "Behavioral/posture anomaly percentile relative to a synthetic normal reference; not a compromise probability.",
    }
