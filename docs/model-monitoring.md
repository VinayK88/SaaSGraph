# Model Monitoring and Robustness Testing

SaaSGraph monitors the feature population feeding its Isolation Forest separately from the deterministic OAuth consent and scope-risk rules.

## Population drift monitoring

`saasgraph.evaluation.population_drift_report` computes Population Stability Index (PSI) for every ML feature. The default alert threshold is `0.20` per feature.

The monitoring suite includes:

- a steady-state reference-to-reference comparison that should remain stable;
- a deterministic synthetic shifted population with higher user reach, API intensity, token persistence, and administrative consent that should trigger drift.

The report also publishes the model version (`saasgraph-iforest-v1`), feature schema (`oauth-behavior-v1`), random seed, and report-generation timestamp.

A drift alert means the observed feature population changed materially. It does not prove token abuse or compromise and does not automatically change deterministic policy decisions.

## Robustness testing

The defensive synthetic suite evaluates three subtle posture changes:

1. low-and-slow API growth below the deterministic 3x API threshold;
2. a consent-plus-persistence change;
3. dormant token reactivation with elevated activity.

Each case records the deterministic rule score, anomaly percentile, Isolation Forest outlier state, hybrid priority, and whether it would be surfaced for review.

The reported synthetic surface rate is a reproducibility metric only; it is not production detection recall.

## Safety boundary

All applications, scopes, users, tokens, API volumes, and resources are synthetic. The suite does not authenticate to a SaaS tenant, retrieve tokens, or modify consent.
