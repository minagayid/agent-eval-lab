# Reliable Agentic AI for High-Stakes Systems — implementation ledger

Updated 2026-09-30. This ledger distinguishes working local contracts from research requiring data, compute, identity integration or external validation. Completion of a scaffold does not complete its research gate.

| Priority / milestone | Working implementation or existing evidence | Remaining acceptance gate |
|---|---|---|
| P0 M1 foundations | Local-first source, README scope, bounded inputs, existing project tests, synthetic fixtures | Pin research dataset/model versions in each real experiment; verify container deployments |
| P0 M2 evaluation | 100 fixture variants, strict predictions, trace scoring, 14-code taxonomy, JSON/HTML, SQLite, FastAPI, React, regression CI | Capture real agent predictions, independent labels for groundedness/injection/conflict, tokens/cost; verify PostgreSQL |
| P0 M3 Personizer | Fixed skills, explicit plan/state, allowlists, exact single-use local approvals, step/repeat limits, trace export, API privilege checks | Authenticated reviewer identity, crash-safe durable state, trusted eval trace bridge, sandboxed generated skills |
| P0 M3 NovaDB | Provenance metadata, bounded TTL, namespace/session visibility, cross-scope overwrite rejection, reopen/TTL tests | Session-bound credential enforcement, crash/process-kill recovery workload, SQLite/PostgreSQL/NovaDB comparable semantic benchmark, scale beyond bounded API candidate window |
| P0 M4 ELLM | Existing pinned SmolLM2 base, training/data manifests, split hashes, adapter card, independent promotion gate; rejected adapter disclosed | Reproduce training on provisioned hardware, held-out real tasks, Arabic/English evaluations, safety remediation; no model promotion before gate |
| P0 M5 dental radiographs | Existing weak-label quality-regression nested folds; new patient/image split validator and reproducible image-level MAE bootstrap helper | Actual pseudonymous patient identities, consent/license, expert labels, patient-clustered CIs, external cohort, clinically appropriate endpoints/calibration and review |
| P1 M5 healthcare workflow | Personizer synthetic protocol/review seam, role/approval controls, private-summary memory and audit APIs in NovaDB | End-to-end authenticated orchestration, human sign-off, redaction tests and threat model; synthetic data only until authorized |
| P1 M6 Genopedia | Existing versioned manifests/catalog hashing; lexical evidence retrieval with source URL/version/license/hash and precision/recall/MRR | Licensed independent retrieval/ranking set, RefSeq 237 manifest checks, measured baselines and scientific review; no sequence editing |
| P1 M6 Neurapedia | Existing research-only imaging pipeline; Dice/IoU/error counts, Brier/ECE/entropy metric functions | Permission-bound independent segmentation masks, patient splits, noise/motion/OOD cohorts, uncertainty validation; no diagnostic deployment |
| P1 M7 robotic surgery | Existing safety supervisor/replay; eight deterministic control/fault checks for dropout, latency, dimensions, workspace, controller source, emergency stop and replay | Richer collision/workspace simulation, perturbation sweeps, formal timing/threat analysis; no physical device execution or clinical claim |
| P0 M8 portfolio | Featured evidence-backed repositories, benchmark page, research note, honest publication status, CV and remote-only availability | Independent reproduction, real-agent results, peer review when earned |
| P2 opportunities | Named roles checked against official pages and remote-only preference | Four listed roles are office-based; Residency 2026 closed. No eligible named application submitted |

## Backlog conventions

Use P0/P1/P2 and the M1–M8 references in issue bodies. Suggested labels: architecture, ai, agents, evaluation, safety, benchmark, research, docs, tests, perf, security. Only use repository labels/milestones that actually exist; do not claim GitHub milestones were created when the evidence is issue checklists.

Each future experiment must record commit, environment, dataset version/hash/license, patient or subject split where applicable, baseline, metric denominators, failed cases and uncertainty. Run a meaningful check before claiming a gate complete. Avoid fabricated metrics, synthetic clinical ground truth, unsupported superiority or autonomous consequential action.
