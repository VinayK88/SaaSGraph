# Security and evaluation boundary

SaaSGraph is a **defensive, synthetic portfolio project**. It does not authenticate to Microsoft 365, Google Workspace, GitHub, Slack, Salesforce, ServiceNow, or any other production SaaS tenant.

The checked-in fixtures contain invented application names, consent grants, scopes, user counts, token characteristics, API volumes, and resource relationships. No real credentials, refresh tokens, customer data, tenant identifiers, or employee identities are included.

The project does not revoke tokens, disable applications, alter consent, enumerate live tenant data, or execute destructive response actions. Recommendations are explanatory outputs only.

Risk scores are transparent project heuristics for demonstrating engineering design. They are not breach probabilities, vendor scores, compliance certifications, or production security guarantees.

A production implementation would require authorized read-only provider integrations, privacy review, tenant-specific baselines, app-owner workflows, tested incident-response procedures, audit logging, and human approval before access-changing actions.
