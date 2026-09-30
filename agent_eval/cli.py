import argparse
import json
from pathlib import Path

from .reporting import write_report
from .runner import benchmark, compare


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", default="datasets/tasks/synthetic.jsonl")
    parser.add_argument("--agent", choices=["v1", "v2"], default="v2")
    parser.add_argument(
        "--predictions",
        help="JSON array of external agent predictions; never contains gold labels",
    )
    parser.add_argument("--output", default="reports/latest")
    parser.add_argument(
        "--compare", help="Compare against a prior report; fail on success regressions"
    )
    args = parser.parse_args()
    report = benchmark(
        args.tasks,
        args.agent,
        json.loads(Path(args.predictions).read_text()) if args.predictions else None,
    )
    write_report(report, args.output)
    print(
        json.dumps(
            {"tasks": report["task_count"], "summary": report["summary"]}, indent=2
        )
    )
    if args.compare:
        changes = compare(json.loads(Path(args.compare).read_text()), report)
        print(json.dumps(changes, indent=2))
        if changes["regressed"]:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
