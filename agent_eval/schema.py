"""Strict public task and prediction contracts; gold labels stay with evaluators."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class Call(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tool: str
    arguments: dict[str, Any]


class Task(BaseModel):
    model_config = ConfigDict(extra="forbid")
    task_id: str
    category: str
    prompt: str
    payload: dict[str, Any]
    expected_answer: Any
    expected_calls: list[Call] = Field(default_factory=list)
    expected_citations: list[str] | None = None
    relevant_documents: list[str] | None = None
    forbidden_tools: list[str] = Field(default_factory=list)
    requires_approval: bool = False
    inject_transient_failure: bool = False

    def public_input(self) -> dict[str, Any]:
        return self.model_dump(include={"task_id", "category", "prompt", "payload"})


class Event(BaseModel):
    model_config = ConfigDict(extra="forbid")
    timestamp: str
    tool: str
    arguments: dict[str, Any]
    result: Any = None
    status: Literal["ok", "error", "blocked"]
    error: str | None = None
    latency_ms: float = Field(ge=0)


class Prediction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    task_id: str
    agent_id: str
    answer: Any
    trace: list[Event] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)
    retrieved_documents: list[str] = Field(default_factory=list)
    authorized: bool = False
    latency_ms: float = Field(ge=0)
    tokens: int | None = Field(default=None, ge=0)
    cost_usd: float | None = Field(default=None, ge=0)
