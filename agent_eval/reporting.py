import html
import json
from pathlib import Path


def write_report(report, output):
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.with_suffix(".json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False)
    )
    rows = "".join(
        f"<tr><td>{html.escape(r['task_id'])}</td><td>{html.escape(r['category'])}</td><td>{r['success']}</td><td>{html.escape(', '.join(r['failures']))}</td></tr>"
        for r in report["rows"]
    )
    summary = html.escape(json.dumps(report["summary"], indent=2))
    path.with_suffix(".html").write_text(
        f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Agent evaluation report</title><style>body{{font:16px system-ui;max-width:1100px;margin:40px auto;padding:20px}}table{{border-collapse:collapse;width:100%}}td,th{{padding:8px;text-align:left;border-bottom:1px solid #ddd}}pre{{overflow:auto}}</style><h1>{html.escape(report["agent"])} evaluation</h1><p>{html.escape(report["scope"])}</p><p>Tasks: {report["task_count"]} · Dataset SHA-256: {report["dataset_sha256"]}</p><pre>{summary}</pre><table><thead><tr><th>Task</th><th>Category</th><th>Success</th><th>Observed failures</th></tr></thead><tbody>{rows}</tbody></table></html>'
    )
