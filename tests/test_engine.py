import unittest

from saasgraph.engine import assess, blast_radius
from saasgraph.fixtures import apps
from saasgraph.models import RiskLevel
from saasgraph.report import build_report


class SaaSGraphTests(unittest.TestCase):
    def test_expected_levels_match(self):
        for app in apps():
            self.assertEqual(assess(app).risk_level, app.expected_level)

    def test_analytics_sync_is_critical(self):
        item = next(a for a in apps() if a.app_id == "app-002")
        result = assess(item)
        self.assertEqual(result.risk_level, RiskLevel.CRITICAL)
        self.assertEqual(result.risk_score, 100)
        self.assertGreater(result.api_ratio, 100)

    def test_dormant_app_is_high_risk(self):
        item = next(a for a in apps() if a.app_id == "app-003")
        result = assess(item)
        self.assertEqual(result.risk_level, RiskLevel.HIGH_RISK)
        self.assertIn("dormant application still retains access", result.reasons)

    def test_low_scope_app_stays_normal(self):
        item = next(a for a in apps() if a.app_id == "app-004")
        self.assertEqual(assess(item).risk_level, RiskLevel.NORMAL)

    def test_blast_radius_counts(self):
        item = next(a for a in apps() if a.app_id == "app-007")
        graph = blast_radius(item)
        self.assertEqual(graph["users"], 400)
        self.assertEqual(graph["nodes"], 404)

    def test_report_summary(self):
        summary = build_report()["summary"]
        self.assertEqual(summary["applications"], 8)
        self.assertEqual(summary["expected_outcomes_matched"], 8)
        self.assertEqual(summary["critical"], 2)
        self.assertEqual(summary["high_risk"], 2)

    def test_all_scores_are_bounded(self):
        for app in apps():
            self.assertGreaterEqual(assess(app).risk_score, 0)
            self.assertLessEqual(assess(app).risk_score, 100)

    def test_recommendations_exist(self):
        for app in apps():
            self.assertTrue(assess(app).recommended_actions)


if __name__ == "__main__":
    unittest.main()
