from __future__ import annotations

from collections import Counter

from .engine import assess, blast_radius
from .evaluation import evaluation_summary
from .fixtures import apps
from .ml import analyze_apps, ml_summary


def build_report() -> dict:
    inventory = apps()
    assessments = [assess(app) for app in inventory]
    ml_findings = analyze_apps(inventory)
    levels = Counter(a.risk_level.value for a in assessments)
    matched = sum(a.risk_level == app.expected_level for a, app in zip(assessments, inventory))
    mean_risk = round(sum(a.risk_score for a in assessments) / len(assessments), 1)
    highest = max(assessments, key=lambda a: a.risk_score)
    exposed_users = sum(a.users_exposed for a in assessments if a.risk_level.value in {"HIGH_RISK", "CRITICAL"})

    return {
        "summary": {
            "applications": len(inventory),
            "expected_outcomes_matched": matched,
            "critical": levels["CRITICAL"],
            "high_risk": levels["HIGH_RISK"],
            "review": levels["REVIEW"],
            "normal": levels["NORMAL"],
            "mean_risk_score": mean_risk,
            "users_behind_high_risk_or_critical_grants": exposed_users,
            "highest_risk_app": highest.name,
            "highest_risk_score": highest.risk_score,
        },
        "ml": ml_summary(inventory),
        "ml_findings": [row.to_dict() for row in ml_findings],
        "model_monitoring_and_robustness": evaluation_summary(inventory),
        "assessments": [a.to_dict() for a in assessments],
        "blast_radius": [blast_radius(app) for app in inventory],
        "boundary": "Synthetic, defensive portfolio data only; rule and ML scores are not production compromise probabilities.",
    }
