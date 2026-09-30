import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from agents.scripted import run

from .evaluator import score
from .schema import Prediction, Task


def load_tasks(path):
    tasks = [
        Task.model_validate(json.loads(line))
        for line in Path(path).read_text().splitlines()
        if line.strip()
    ]
    if not tasks or len(tasks) > 10000 or len({t.task_id for t in tasks}) != len(tasks):
        raise ValueError("Tasks must have unique IDs and number 1–10000")
    return tasks


def benchmark(path, version="v2", predictions=None):
    tasks = load_tasks(path)
    if predictions is not None:
        parsed = [Prediction.model_validate(p) for p in predictions]
        if len(parsed) != len(tasks) or len({p.task_id for p in parsed}) != len(parsed):
            raise ValueError("Exactly one prediction per task is required")
        by_id = {p.task_id: p for p in parsed}
        if set(by_id) != {t.task_id for t in tasks}:
            raise ValueError("Prediction set differs from task set")
    rows = [
        score(
            t,
            by_id[t.task_id]
            if predictions is not None
            else run(t.public_input(), version, t.inject_transient_failure),
        )
        for t in tasks
    ]
    summary = {"task_success_rate": sum(r["success"] for r in rows) / len(rows)}
    for key in rows[0]["metrics"]:
        vals = [r["metrics"][key] for r in rows if r["metrics"][key] is not None]
        summary[key] = sum(vals) / len(vals) if vals else None
        summary[key + "_n"] = len(vals)
    return {
        "schema_version": 1,
        "generated_at": datetime.now(UTC).isoformat(),
        "dataset_sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest(),
        "agent": "external-predictions"
        if predictions is not None
        else "scripted-" + version,
        "scope": "synthetic local control benchmark; not evidence of LLM or clinical capability",
        "task_count": len(rows),
        "summary": summary,
        "rows": rows,
    }


def compare(before, after):
    if before["dataset_sha256"] != after["dataset_sha256"]:
        raise ValueError("Cannot compare different dataset versions")
    old = {r["task_id"]: r["success"] for r in before["rows"]}
    new = {r["task_id"]: r["success"] for r in after["rows"]}
    if set(old) != set(new):
        raise ValueError("Cannot compare different task populations")
    regressed = sorted(k for k in old if old[k] and not new[k])
    improved = sorted(k for k in old if not old[k] and new[k])
    return {
        "regressed": regressed,
        "improved": improved,
        "regression_rate": len(regressed) / len(old),
    }
