"""Local API for fixed synthetic tasks only. No arbitrary tools, prompts, or code execution."""

from pathlib import Path
from typing import Literal

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict

from .runner import benchmark
from .storage import store_report

ROOT = Path(__file__).resolve().parents[1]
app = FastAPI(title="Agent Evaluation Lab", version="0.1.0")


class RunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    agent: Literal["v1", "v2"] = "v2"


@app.get("/health")
def health():
    return {"status": "ok", "mode": "local-synthetic-evaluation"}


@app.post("/api/runs")
def evaluate(request: RunRequest):
    report = benchmark(ROOT / "datasets/tasks/synthetic.jsonl", request.agent)
    return {"run_id": store_report(report), "report": report}


if (ROOT / "web/dist").exists():
    app.mount(
        "/", StaticFiles(directory=ROOT / "web/dist", html=True), name="dashboard"
    )
