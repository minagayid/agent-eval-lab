"""Local results store; SQLite default, optional PostgreSQL via DATABASE_URL."""

import json
import os
import sqlite3
import uuid


def store_report(report):
    run_id = str(uuid.uuid4())
    url = os.environ.get("DATABASE_URL", "")
    if url:
        import psycopg

        with psycopg.connect(url) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS evaluation_runs (id TEXT PRIMARY KEY, report TEXT NOT NULL)"
            )
            conn.execute(
                "INSERT INTO evaluation_runs VALUES (%s, %s)",
                (run_id, json.dumps(report)),
            )
    else:
        with sqlite3.connect(
            os.environ.get("EVAL_DB_PATH", "evaluation.sqlite3")
        ) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS evaluation_runs (id TEXT PRIMARY KEY, report TEXT NOT NULL)"
            )
            conn.execute(
                "INSERT INTO evaluation_runs VALUES (?, ?)",
                (run_id, json.dumps(report)),
            )
    return run_id
