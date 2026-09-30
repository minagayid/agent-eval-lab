# Agent Eval Lab

Trace-based evaluation and failure analysis for tool-using agents. A local FastAPI API, React dashboard, JSON/HTML reports, and regression gate make agent behavior inspectable.

**Measured scope:** 100 synthetic fixture variants across ten categories. The supplied v1/v2 agents are scripted controls and receive explicit tool requests, not gold answers. This checks evaluator behavior; it is not a benchmark of an LLM's reasoning, autonomous planning, prompt-injection resistance or clinical capability.

## Reproduce

    python -m venv .venv
    . .venv/bin/activate
    pip install -e '.[dev]'
    make test lint benchmark
    cd web
    npm ci
    npm run build
    cd ..
    make run

Open http://127.0.0.1:8000. The /api/runs endpoint persists a control run to SQLite by default. DATABASE_URL selects the optional psycopg PostgreSQL store; docker compose up --build provides a development PostgreSQL stack. Docker/PostgreSQL execution has not been verified in the authoring environment.

## Observed controls

| Metric | v1 | v2 | Eligible fixtures |
|---|---:|---:|---:|
| Task success | 50/100 | 100/100 | 100 |
| Citation accuracy | 0% | 100% | 20 |
| Transient recovery | 0/10 | 10/10 | 10 |
| Unauthorized attempts | 10/100 | 0/100 | 100 |
| Success regressions v1 → v2 | — | 0 | 100 |

See reports/baseline.json, reports/latest.json, and reports/latest.html. Ten templates have ten fixture variants each; these are not 100 independent difficult tasks. Latency is measured on the local runner and is not a cross-machine performance claim. Token counts, monetary cost, hallucination and groundedness remain null when unobserved. Recovery denominators include the ten labeled transient-failure cases, not unrelated permission errors.

## External predictions

    python -m agent_eval.cli --tasks datasets/tasks/synthetic.jsonl --predictions predictions.json --output reports/external
    python -m agent_eval.cli --agent v2 --compare reports/baseline.json

predictions.json is an array matching Prediction in agent_eval/schema.py, exactly one record per task. Keep gold labels inside the evaluator; agents receive Task.public_input(). External approval assertions and traces are supplied evidence, not independently authenticated. Real system adapters need trustworthy trace capture and reviewer authorization evidence before security claims.

Scoring checks exact expected answers and successful calls, citation precision/completeness, retrieval relevance, unauthorized attempts, execution errors and transient recovery. A correct answer cannot cancel an unauthorized attempt or an invented citation. Fourteen failure codes include labeled-data requirements; unobserved conflict, injection and hallucination failures are not inferred.

## Portfolio integration

Clone Personizer, NovaDB, Genopedia, Neurapedia and robotic-surgery next to this repository, install their documented dependencies, then run:

    python benchmarks/portfolio_contracts.py --repos ..

The local report at reports/portfolio-contracts.json covers actual workflow/permissions, memory isolation/reopen, lexical source provenance, metric contracts and eight simulator faults. It records base commits and dirty working trees; it does not claim released builds were independently reproduced.

## Next gates

See ROADMAP.md for every workstream from the portfolio roadmap. Real LLM comparisons, independently labeled datasets, prompt-injection scenarios, authenticated approvals, PostgreSQL/Docker execution and clinical/device validation remain separate evidence gates.
