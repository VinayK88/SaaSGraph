# SaaSGraph ML anomaly methodology

SaaSGraph uses a hybrid design: OAuth consent/scope policy remains deterministic, while an unsupervised behavioral model prioritizes integrations that look unusual relative to a deterministic synthetic normal-reference population.

## Model

The ML layer uses `IsolationForest` with 800 seeded synthetic reference profiles. The reference generator models ordinary scope breadth, user reach, token persistence, dormancy, API-rate variation, resource reach, publisher verification, admin consent, and external-tenant relationships.

## Features

- deterministic scope-risk score;
- scope count and sensitive-scope count;
- log user reach;
- persistent refresh-token state;
- log dormancy;
- log observed/baseline API ratio;
- resource count;
- publisher verification;
- admin consent;
- external-tenant boundary.

For each application the model returns an anomaly percentile, outlier flag, top feature deviations, and a bounded hybrid review priority. The original OAuth rule score remains visible and is never replaced by the ML model.

## Boundary

Anomaly percentiles are not compromise probabilities. All data is synthetic. A production model should be trained and evaluated on authorized tenant telemetry, segmented by application role, monitored for drift, and calibrated against analyst dispositions and incident outcomes.
