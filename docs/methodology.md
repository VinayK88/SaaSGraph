# SaaSGraph methodology

## Objective

SaaSGraph models third-party SaaS and OAuth exposure as a combination of **permission sensitivity, consent scope, token persistence, publisher trust, user reach, resource reach, inactivity, cross-tenant trust, and observed API behavior**.

## Risk model

The project uses a deterministic score from 0 to 100. It deliberately keeps the components inspectable rather than presenting an opaque model probability.

Major signals include:

- sensitive OAuth scopes;
- administrative consent;
- unverified publisher state;
- persistent refresh-token access;
- number of users behind the grant;
- dormant applications retaining access;
- API-call volume relative to a deterministic baseline;
- number of downstream resources; and
- third-party tenant boundaries.

Thresholds map the score into `NORMAL`, `REVIEW`, `HIGH_RISK`, and `CRITICAL`.

## Blast radius

The graph representation treats an application as a trust node connected to users, resources, and scopes. The current implementation intentionally keeps graph metrics simple and auditable. A production implementation could add identity-group expansion, nested SaaS-to-SaaS relationships, resource sensitivity, service principals, application roles, sign-in provenance, and historical token/session evidence.

## Evaluation

The baseline contains eight deterministic synthetic applications spanning benign, review-worthy, high-risk, and critical patterns. Expected outcomes are checked by unit tests and CI.

The baseline exists to verify code behavior and reviewer reproducibility. It does not estimate real-world false-positive rates or incident prevalence.
