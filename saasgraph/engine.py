from __future__ import annotations

from .models import Assessment, OAuthApp, RiskLevel

SCOPE_WEIGHTS = {
    "user.read": 2,
    "calendars.read": 4,
    "contacts.read": 6,
    "offline_access": 6,
    "repo.read": 7,
    "directory.read.all": 8,
    "mail.read": 8,
    "files.read.all": 10,
    "sites.read.all": 10,
    "chat.read": 9,
    "channels.read.all": 10,
}


def _user_score(users: int) -> int:
    if users > 250:
        return 10
    if users > 50:
        return 7
    if users > 20:
        return 5
    if users > 5:
        return 3
    return 0


def _api_ratio(app: OAuthApp) -> float:
    baseline = max(1, app.baseline_api_calls_per_hour)
    return round(app.observed_api_calls_per_hour / baseline, 2)


def _level(score: int) -> RiskLevel:
    if score >= 75:
        return RiskLevel.CRITICAL
    if score >= 50:
        return RiskLevel.HIGH_RISK
    if score >= 25:
        return RiskLevel.REVIEW
    return RiskLevel.NORMAL


def assess(app: OAuthApp) -> Assessment:
    scope_risk = min(30, sum(SCOPE_WEIGHTS.get(scope, 5) for scope in app.scopes))
    ratio = _api_ratio(app)
    score = scope_risk
    reasons: list[str] = []
    actions: list[str] = []

    if scope_risk >= 20:
        reasons.append("broad or sensitive OAuth scopes")
        actions.append("review least-privilege scope requirements")
    if not app.publisher_verified:
        score += 12
        reasons.append("publisher is not verified")
        actions.append("validate publisher ownership and application provenance")
    if app.admin_consent:
        score += 12
        reasons.append("tenant-wide or administrative consent")
        actions.append("reconfirm business owner and admin-consent necessity")
    if app.token_persistent:
        score += 8
        reasons.append("persistent refresh-token access")
        actions.append("review token lifetime and revoke stale grants")

    score += _user_score(app.users)

    if app.dormant_days >= 90:
        score += 8
        reasons.append("dormant application still retains access")
        actions.append("remove unused grants and disable dormant integrations")
    elif app.dormant_days >= 30:
        score += 4
        reasons.append("application has been inactive for an extended period")

    if ratio >= 20:
        score += 18
        reasons.append("extreme API-volume deviation from baseline")
        actions.append("investigate token use and bulk data access immediately")
    elif ratio >= 8:
        score += 12
        reasons.append("large API-volume deviation from baseline")
        actions.append("investigate recent API and download activity")
    elif ratio >= 3:
        score += 6
        reasons.append("API-volume deviation from baseline")

    score += min(8, len(app.resources) * 2)

    if app.external_tenant:
        score += 6
        reasons.append("third-party tenant trust boundary")
        actions.append("review cross-tenant data-access expectations")

    if not app.publisher_verified and app.admin_consent and app.token_persistent and scope_risk >= 20:
        score += 8
        reasons.append("high-risk consent and persistence combination")

    score = min(100, score)
    level = _level(score)

    if level is RiskLevel.CRITICAL:
        actions.insert(0, "consider immediate token revocation pending investigation")
    elif level is RiskLevel.HIGH_RISK:
        actions.insert(0, "prioritize security review of the application grant")

    if not actions:
        actions.append("continue normal monitoring and periodic access review")

    return Assessment(
        app_id=app.app_id,
        name=app.name,
        risk_level=level,
        risk_score=score,
        scope_risk=scope_risk,
        api_ratio=ratio,
        users_exposed=app.users,
        resources_reachable=len(app.resources),
        reasons=tuple(dict.fromkeys(reasons)),
        recommended_actions=tuple(dict.fromkeys(actions)),
    )


def blast_radius(app: OAuthApp) -> dict:
    return {
        "app_id": app.app_id,
        "app": app.name,
        "users": app.users,
        "resources": list(app.resources),
        "scopes": list(app.scopes),
        "nodes": 1 + app.users + len(app.resources),
        "edges": app.users + len(app.resources) + len(app.scopes),
    }
