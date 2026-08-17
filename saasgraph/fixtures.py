"""Deterministic synthetic OAuth application fixtures for defensive evaluation."""

from .models import OAuthApp, RiskLevel


def apps() -> tuple[OAuthApp, ...]:
    return (
        OAuthApp("app-001", "PayrollConnector", "Synthetic HR Publisher", True, True, ("user.read", "offline_access"), 20, True, 0, 100, 110, ("profile", "payroll"), False, RiskLevel.REVIEW),
        OAuthApp("app-002", "AnalyticsSync", "Synthetic External Publisher", False, True, ("files.read.all", "sites.read.all", "offline_access"), 247, True, 2, 120, 18420, ("sharepoint", "onedrive", "m365"), True, RiskLevel.CRITICAL),
        OAuthApp("app-003", "LegacyExport", "Synthetic Internal IT", True, True, ("directory.read.all", "offline_access"), 80, True, 180, 1, 0, ("directory", "identity"), False, RiskLevel.HIGH_RISK),
        OAuthApp("app-004", "CalendarHelper", "Synthetic Calendar Publisher", True, False, ("calendars.read",), 15, False, 2, 50, 55, ("calendar",), False, RiskLevel.NORMAL),
        OAuthApp("app-005", "SupportTools", "Synthetic External Integrator", False, False, ("mail.read", "contacts.read", "offline_access"), 44, True, 1, 20, 180, ("mail", "contacts"), True, RiskLevel.HIGH_RISK),
        OAuthApp("app-006", "BuildBot", "Synthetic Engineering Platform", True, True, ("repo.read", "offline_access"), 8, True, 0, 200, 220, ("github", "release-metadata"), False, RiskLevel.REVIEW),
        OAuthApp("app-007", "MigrationAssistant", "Synthetic Migration Publisher", True, True, ("files.read.all", "mail.read", "offline_access"), 400, True, 0, 100, 3200, ("mail", "onedrive", "sharepoint"), False, RiskLevel.CRITICAL),
        OAuthApp("app-008", "NotesLite", "Synthetic Small Publisher", False, False, ("user.read",), 3, False, 10, 10, 9, ("profile",), True, RiskLevel.NORMAL),
    )
