"""Bounded local tools. No shell, network, medical actions, or arbitrary SQL."""

import sqlite3

TOOL_SCHEMAS = {
    "calculator": {"a": "number", "b": "number"},
    "retrieval": {"query": "string", "documents": "list"},
    "database": {"minimum": "integer"},
    "document": {"text": "string"},
    "sort": {"values": "list"},
    "plan": {"dependencies": "object"},
}


def execute(name, arguments):
    if name not in TOOL_SCHEMAS:
        raise PermissionError("Tool is not allowlisted")
    if set(arguments) != set(TOOL_SCHEMAS[name]):
        raise ValueError("Tool argument keys do not match schema")
    if name == "calculator":
        a, b = arguments["a"], arguments["b"]
        if any(isinstance(v, bool) or not isinstance(v, (float, int)) for v in (a, b)):
            raise ValueError("Calculator expects numbers")
        return a + b
    if name == "retrieval":
        query = str(arguments["query"]).lower().split()
        docs = arguments["documents"]
        if len(docs) > 100:
            raise ValueError("Too many documents")
        scored = [(sum(t in d["text"].lower() for t in query), d) for d in docs]
        matches = sorted(scored, key=lambda v: (-v[0], v[1]["id"]))
        return [d for score, d in matches if score > 0][:3]
    if name == "database":
        minimum = arguments["minimum"]
        if type(minimum) is not int:
            raise ValueError("Minimum must be integer")
        with sqlite3.connect(":memory:") as conn:
            conn.execute("CREATE TABLE items (id INTEGER PRIMARY KEY)")
            conn.executemany("INSERT INTO items VALUES (?)", [(i,) for i in range(10)])
            return conn.execute(
                "SELECT COUNT(*) FROM items WHERE id >= ?", (minimum,)
            ).fetchone()[0]
    if name == "document":
        text = arguments["text"]
        if not isinstance(text, str) or len(text) > 10000:
            raise ValueError("Invalid document")
        return len(text.split())
    if name == "sort":
        values = arguments["values"]
        if (
            not isinstance(values, list)
            or len(values) > 100
            or any(type(v) is not int for v in values)
        ):
            raise ValueError("Expected at most 100 integers")
        return sorted(values)
    deps = arguments["dependencies"]
    if not isinstance(deps, dict) or len(deps) > 100:
        raise ValueError("Invalid dependencies")
    result = []
    while len(result) < len(deps):
        ready = sorted(
            k
            for k, vs in deps.items()
            if k not in result and all(v in result for v in vs)
        )
        if not ready:
            raise ValueError("Cyclic or missing dependencies")
        result.extend(ready)
    return result
