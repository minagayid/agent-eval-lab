"""Run actual sibling project contracts on synthetic fixtures.

Clone the five named sibling repositories beside agent-eval-lab. This adapter
does not install packages, fetch datasets, call a model or execute a real action.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repos", type=Path, default=Path(__file__).resolve().parents[2]
    )
    parser.add_argument(
        "--output", type=Path, default=Path("reports/portfolio-contracts.json")
    )
    args = parser.parse_args()
    names = (
        "personizer",
        "novadb-engine",
        "genopedia",
        "neurapedia",
        "robotic-surgery",
    )
    roots = {name: args.repos.resolve() / name for name in names}
    revisions = {}
    for name, root in roots.items():
        if not (root / ".git").exists():
            raise ValueError(f"Missing local clone: {name}")
        sys.path.insert(0, str(root))
        revisions[name] = {
            "base_commit": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=root, text=True
            ).strip(),
            "working_tree_modified": bool(
                subprocess.check_output(
                    ["git", "status", "--porcelain"], cwd=root, text=True
                ).strip()
            ),
        }
    from app.runtime import Runtime
    from genopedia.evidence import EvidenceDocument, retrieval_metrics, retrieve
    from neurapedia.evaluation import probability_metrics, segmentation_metrics
    from novadb.engine import Engine
    from novadb.memory import MemoryStore
    from robotic_surgery.fault_benchmark import run_fault_benchmark

    rows = []
    workflow = Runtime().run(
        [
            {"tool": "retrieve_protocol", "arguments": {"fixture_id": "fixture-001"}},
            {"tool": "request_review", "arguments": {"fixture_id": "fixture-001"}},
        ],
        "eval-session",
    )
    denied = Runtime().run(
        [{"tool": "simulate_schedule", "arguments": {"fixture_id": "fixture-001"}}],
        "eval-session",
    )
    rows.append(
        {
            "project": "personizer",
            "check": "workflow_and_permissions",
            "passed": workflow["state"] == "completed" and denied["state"] == "blocked",
            "trace": workflow["trace"],
            "blocked_trace": denied["trace"],
        }
    )
    with tempfile.TemporaryDirectory() as directory:
        engine = Engine(directory)
        store = MemoryStore(engine)
        store.upsert(
            {
                "namespace": "benchmark",
                "session_id": "a",
                "content": "Synthetic evidence",
                "source": "fixture-v1",
                "metadata": {"content_sha256": "fixture-only"},
            }
        )
        hidden = (
            store.recent({"namespace": "benchmark", "session_id": "b"})["count"] == 0
        )
        engine.close()
        engine = Engine(directory)
        restored = MemoryStore(engine).recent(
            {"namespace": "benchmark", "session_id": "a"}
        )
        rows.append(
            {
                "project": "novadb-engine",
                "check": "isolation_and_durable_reopen",
                "passed": hidden and restored["count"] == 1,
                "provenance": restored["memories"][0]["source"],
            }
        )
        engine.close()
    docs = [
        EvidenceDocument(
            "fixture-a",
            "https://example.org/a",
            "synthetic-v1",
            "protein annotation provenance",
            "synthetic",
        ),
        EvidenceDocument(
            "fixture-b",
            "https://example.org/b",
            "synthetic-v1",
            "neuroimaging segmentation",
            "synthetic",
        ),
    ]
    found = retrieve("protein annotation", docs)
    metrics = retrieval_metrics([d["source_id"] for d in found], {"fixture-a"})
    rows.append(
        {
            "project": "genopedia",
            "check": "lexical_source_retrieval",
            "passed": metrics["recall"] == 1.0,
            "metrics": metrics,
            "retrieved_sources": [
                {k: v for k, v in d.items() if k != "text"} for d in found
            ],
        }
    )
    overlap = segmentation_metrics([1, 1, 0], [1, 0, 1])
    probability = probability_metrics([0.0, 1.0], [0, 1])
    rows.append(
        {
            "project": "neurapedia",
            "check": "metric_contract",
            "passed": overlap["dice"] == 0.5 and probability["brier_score"] == 0.0,
            "metrics": {**overlap, **probability},
        }
    )
    faults = run_fault_benchmark()
    rows.append(
        {
            "project": "robotic-surgery",
            "check": "fault_injection",
            "passed": faults["passed"] == faults["case_count"],
            "report": faults,
        }
    )
    result = {
        "scope": "five local synthetic contract checks; not real agent, clinical, scientific or hardware performance",
        "revisions": revisions,
        "checks": rows,
        "passed": sum(row["passed"] for row in rows),
        "count": len(rows),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"passed": result["passed"], "count": result["count"]}))
    if result["passed"] != result["count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
