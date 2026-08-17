import unittest

from saasgraph.fixtures import apps
from saasgraph.ml import FEATURE_NAMES, MODEL_NAME, analyze_apps, feature_vector, ml_summary


class SaaSGraphMLTests(unittest.TestCase):
    def test_feature_shape(self):
        self.assertEqual(len(feature_vector(apps()[0])), len(FEATURE_NAMES))

    def test_model_metadata(self):
        summary = ml_summary(apps())
        self.assertEqual(summary["model"], MODEL_NAME)
        self.assertEqual(summary["normal_reference_samples"], 800)

    def test_extreme_api_behavior_is_prioritized(self):
        rows = {row.app_id: row for row in analyze_apps(apps())}
        self.assertGreater(rows["app-002"].anomaly_percentile, rows["app-004"].anomaly_percentile)
        self.assertGreater(rows["app-002"].hybrid_priority, rows["app-004"].hybrid_priority)

    def test_normal_calendar_helper_is_below_critical_apps(self):
        rows = {row.app_id: row for row in analyze_apps(apps())}
        self.assertLess(rows["app-004"].hybrid_priority, rows["app-007"].hybrid_priority)

    def test_deterministic_results(self):
        first = [row.to_dict() for row in analyze_apps(apps())]
        second = [row.to_dict() for row in analyze_apps(apps())]
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
