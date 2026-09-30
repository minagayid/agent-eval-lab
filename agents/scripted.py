"""Two deterministic control agents. They receive no gold answers or evaluator flags."""

from datetime import UTC, datetime
from time import perf_counter

from agent_eval.schema import Event, Prediction
from agent_eval.tools import execute


def run(public_task, version="v2", transient=False):
    start = perf_counter()
    payload = public_task["payload"]
    trace, citations, retrieved = [], [], []
    guarded = version == "v2"
    tool = payload.get("tool")
    arguments = payload.get("arguments", {})
    answer = "I cannot determine that from the supplied evidence."
    if (
        tool
        and tool
        not in {"calculator", "retrieval", "database", "document", "sort", "plan"}
        and guarded
    ):
        trace.append(
            Event(
                timestamp=datetime.now(UTC).isoformat(),
                tool=tool,
                arguments=arguments,
                status="blocked",
                error="not_allowlisted",
                latency_ms=0,
            )
        )
        answer = "Action requires human approval."
    elif tool:
        for attempt in range(2 if guarded else 1):
            tick = perf_counter()
            try:
                if transient and attempt == 0:
                    raise TimeoutError("Injected local transient failure")
                result = execute(tool, arguments)
                trace.append(
                    Event(
                        timestamp=datetime.now(UTC).isoformat(),
                        tool=tool,
                        arguments=arguments,
                        result=result,
                        status="ok",
                        latency_ms=(perf_counter() - tick) * 1000,
                    )
                )
                if tool == "retrieval":
                    retrieved = [d["id"] for d in result]
                    citations = retrieved[:1] if guarded else []
                    answer = result[0]["text"] if result else answer
                else:
                    answer = result
                break
            except (ValueError, PermissionError, TimeoutError) as exc:
                trace.append(
                    Event(
                        timestamp=datetime.now(UTC).isoformat(),
                        tool=tool,
                        arguments=arguments,
                        status="error",
                        error=type(exc).__name__,
                        latency_ms=(perf_counter() - tick) * 1000,
                    )
                )
                answer = "Tool failed."
                if not isinstance(exc, TimeoutError):
                    break
    elif not guarded:
        answer = "The answer is certainly 42."
    return Prediction(
        task_id=public_task["task_id"],
        agent_id=f"scripted-{version}",
        answer=answer,
        trace=trace,
        citations=citations,
        retrieved_documents=retrieved,
        latency_ms=(perf_counter() - start) * 1000,
    )
