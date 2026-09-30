# Synthetic healthcare operations orchestrator demo

This deterministic, offline teaching example shows safety controls around one non-clinical administrative workflow. It is not a healthcare product or clinical agent.

## Safety boundaries

- Inputs are fixed synthetic case IDs plus enumerated roles, tools, and reviewer decisions. There is no free-text patient input or patient-record schema.
- Fixtures contain no real people or clinical facts. A hostile-text canary is reduced to a boolean presence flag; no free text is accepted, forwarded, interpreted, or logged. This demonstrates data minimization, not LLM prompt-injection robustness.
- The role-to-tool allowlist exposes local read, proposal, review, and simulated queue-update functions. There are no network, EHR, email, shell, database, or external adapters.
- An agent can propose a fixed queue update. A separate simulated reviewer must approve before an executor changes the in-memory status.
- Audit events contain fixed control values and synthetic IDs. Frozen records are linked with SHA-256 hashes.
- One synthetic fixture fails once before the update. Sequential retry completes once; replay returns the prior result. Concurrent calls are not synchronized.

## Run

From the repository root, using the Python standard library:

    python examples/synthetic_healthcare_orchestrator/demo.py
    python -m unittest discover -s examples/synthetic_healthcare_orchestrator -p 'test_*.py' -v

The in-memory audit chain and simulated reviewer role demonstrate mechanics only. They do not provide durable audit storage, authenticated human identity, production authorization, LLM prompt-injection resistance, HIPAA compliance, or clinical validation. Do not add patient data or connect this demo to live systems.
