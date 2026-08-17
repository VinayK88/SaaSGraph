from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

import numpy as np

from .fixtures import apps
from .ml import (
    FEATURE_NAMES,
    MODEL_NAME,
    RANDOM_STATE,
    _normal_reference,
    analyze_apps,
)
from .models import OAuthApp

MODEL_VERSION = "saasgraph-iforest-v1"
FEATURE_SCHEMA_VERSION = "oauth-behavior-v1"
PSI_ALERT_THRESHOLD = 0.20


def _psi(reference: np.ndarray, current: np.ndarray, bins: int = 8) -> float:
    edges = np.unique(np.quantile(reference, np.linspace(0.0, 1.0, bins + 1)))
    if len(edges) < 3:
        return 0.0
    edges[0] = -np.inf
    edges[-1] = np.inf
    ref_counts, _ = np.histogram(reference, bins=edges)
    cur_counts, _ = np.histogram(current, bins=edges)
    ref_pct = np.clip(ref_counts / max(1, ref_counts.sum()), 1e-6, None)
    cur_pct = np.clip(cur_counts / max(1, cur_counts.sum()), 1e-6, None)
    return round(float(np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct))), 4)


def population_drift_report(reference: np.ndarray, current: np.ndarray) -> dict[str, object]:
    feature_psi = {
        name: _psi(reference[:, i], current[:, i])
        for i, name in enumerate(FEATURE_NAMES)
    }
    alerts = sorted(name for name, value in feature_psi.items() if value >= PSI_ALERT_THRESHOLD)
    return {
        "metric": "population_stability_index",
        "threshold": PSI_ALERT_THRESHOLD,
        "feature_psi": feature_psi,
        "drift_alert": bool(alerts),
        "alert_features": alerts,
    }


def _shifted_reference() -> np.ndarray:
    shifted = _normal_reference().copy()
    count = len(shifted) // 3
    # Simulate a tenant-wide change in API intensity, user reach, token persistence,
    # and administrative consent without using any real tenant data.
    shifted[:count, FEATURE_NAMES.index("log_users")] += 1.0
    shifted[:count, FEATURE_NAMES.index("log_api_ratio")] += 1.2
    shifted[:count, FEATURE_NAMES.index("persistent_token")] = 1.0
    shifted[:count, FEATURE_NAMES.index("admin_consent")] = 1.0
    return shifted


def _robustness_cases(inventory: tuple[OAuthApp, ...]) -> list[tuple[str, OAuthApp]]:
    calendar = next(app for app in inventory if app.name == "CalendarHelper")
    notes = next(app for app in inventory if app.name == "NotesLite")
    payroll = next(app for app in inventory if app.name == "PayrollConnector")
    return [
        (
            "low_and_slow_api_growth",
            replace(
                calendar,
                app_id="eval-low-slow",
                name="LowSlowCalendar",
                observed_api_calls_per_hour=145,
            ),
        ),
        (
            "consent_and_persistence_shift",
            replace(
                notes,
                app_id="eval-consent",
                name="ConsentShift",
                admin_consent=True,
                token_persistent=True,
                users=35,
            ),
        ),
        (
            "dormant_token_reactivation",
            replace(
                payroll,
                app_id="eval-dormant",
                name="DormantReactivation",
                dormant_days=120,
                observed_api_calls_per_hour=280,
            ),
        ),
    ]


def robustness_evaluation(inventory: tuple[OAuthApp, ...] | None = None) -> dict[str, object]:
    baseline = inventory or apps()
    cases = _robustness_cases(baseline)
    findings = analyze_apps((*baseline, *[app for _, app in cases]))
    by_id = {row.app_id: row for row in findings}
    results = []
    for case_name, app in cases:
        row = by_id[app.app_id]
        surfaced = row.rule_score >= 25 or row.ml_outlier or row.anomaly_percentile >= 95.0
        results.append({
            "case": case_name,
            "rule_score": row.rule_score,
            "anomaly_percentile": row.anomaly_percentile,
            "ml_outlier": row.ml_outlier,
            "hybrid_priority": row.hybrid_priority,
            "surfaced_for_review": bool(surfaced),
        })
    surfaced = sum(row["surfaced_for_review"] for row in results)
    return {
        "cases": results,
        "surfaced": surfaced,
        "total": len(results),
        "synthetic_surface_rate": round(surfaced / len(results), 3),
        "meaning": "Synthetic robustness test of subtle OAuth/API posture changes; not measured detection recall on production incidents.",
    }


def evaluation_summary(inventory: tuple[OAuthApp, ...] | None = None) -> dict[str, object]:
    baseline = inventory or apps()
    reference = _normal_reference()
    return {
        "model_metadata": {
            "model": MODEL_NAME,
            "model_version": MODEL_VERSION,
            "feature_schema_version": FEATURE_SCHEMA_VERSION,
            "random_state": RANDOM_STATE,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "steady_state_monitoring": population_drift_report(reference, reference),
        "synthetic_shift_monitoring": population_drift_report(reference, _shifted_reference()),
        "robustness_evaluation": robustness_evaluation(baseline),
    }
