import unittest

from saasgraph.evaluation import (
    _shifted_reference,
    evaluation_summary,
    population_drift_report,
    robustness_evaluation,
)
from saasgraph.fixtures import apps
from saasgraph.ml import _normal_reference


class SaaSGraphEvaluationTests(unittest.TestCase):
    def test_steady_state_has_no_drift(self):
        reference = _normal_reference()
        report = population_drift_report(reference, reference)
        self.assertFalse(report["drift_alert"])
        self.assertTrue(all(value == 0.0 for value in report["feature_psi"].values()))

    def test_shifted_reference_triggers_drift(self):
        reference = _normal_reference()
        report = population_drift_report(reference, _shifted_reference())
        self.assertTrue(report["drift_alert"])
        self.assertGreaterEqual(len(report["alert_features"]), 1)

    def test_robustness_cases_are_bounded(self):
        result = robustness_evaluation(apps())
        self.assertEqual(result["total"], 3)
        self.assertTrue(0.0 <= result["synthetic_surface_rate"] <= 1.0)
        self.assertTrue(all(0 <= row["rule_score"] <= 100 for row in result["cases"]))
        self.assertTrue(all(0 <= row["hybrid_priority"] <= 100 for row in result["cases"]))

    def test_summary_contains_versioned_metadata(self):
        summary = evaluation_summary(apps())
        self.assertEqual(summary["model_metadata"]["model_version"], "saasgraph-iforest-v1")
        self.assertEqual(summary["model_metadata"]["feature_schema_version"], "oauth-behavior-v1")


if __name__ == "__main__":
    unittest.main()
