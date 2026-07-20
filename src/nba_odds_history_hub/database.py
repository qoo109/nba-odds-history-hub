"""SQLite persistence for normalized odds snapshots."""

from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path
from typing import Any, Iterable


DEFAULT_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "sql" / "schema.sql"


def connect_database(path: str | Path) -> sqlite3.Connection:
    db_path = Path(path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(
    path: str | Path, *, schema_path: str | Path = DEFAULT_SCHEMA_PATH
) -> None:
    schema = Path(schema_path).read_text(encoding="utf-8")
    with connect_database(path) as connection:
        connection.executescript(schema)


def insert_snapshot_rows(
    path: str | Path,
    rows: list[dict[str, Any]],
    *,
    matchup_count: int,
    market_count: int,
    note: str | None = None,
) -> dict[str, int]:
    """Insert one normalized import and return inserted/skipped counts."""
    if not rows:
        raise ValueError("rows cannot be empty")

    initialize_database(path)
    first = rows[0]
    raw_sha256 = str(first["raw_sha256"])
    observed_at = str(first["observed_at"])
    ingested_at = str(first["ingested_at"])
    source = str(first["source"])

    columns = [
        "import_id",
        "source",
        "league",
        "sport",
        "source_event_id",
        "market_name",
        "market_type",
        "period",
        "side",
        "participant_id",
        "participant_name",
        "line",
        "american_odds",
        "decimal_odds",
        "raw_implied_probability",
        "observed_at",
        "ingested_at",
        "scheduled_tipoff",
        "cutoff_at",
        "source_version",
        "market_key",
        "is_alternate",
        "raw_sha256",
    ]
    placeholders = ", ".join("?" for _ in columns)
    insert_sql = (
        f"INSERT OR IGNORE INTO odds_snapshots ({', '.join(columns)}) "
        f"VALUES ({placeholders})"
    )

    with connect_database(path) as connection:
        connection.execute(
            """
            INSERT OR IGNORE INTO raw_imports (
                source, observed_at, ingested_at, raw_sha256,
                matchup_count, market_count, normalized_row_count, note
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source,
                observed_at,
                ingested_at,
                raw_sha256,
                matchup_count,
                market_count,
                len(rows),
                note,
            ),
        )
        import_row = connection.execute(
            """
            SELECT import_id FROM raw_imports
            WHERE raw_sha256 = ? AND observed_at = ?
            """,
            (raw_sha256, observed_at),
        ).fetchone()
        if import_row is None:
            raise RuntimeError("Failed to create or locate raw import record")
        import_id = int(import_row["import_id"])

        before = connection.total_changes
        for row in rows:
            values = (
                import_id,
                row.get("source"),
                row.get("league"),
                row.get("sport"),
                row.get("source_event_id"),
                row.get("market_name"),
                row.get("market_type"),
                int(row.get("period") or 0),
                row.get("side") or "",
                row.get("participant_id")
                if row.get("participant_id") is not None
                else -1,
                row.get("participant_name") or "unknown",
                row.get("line") if row.get("line") is not None else -999999.0,
                row.get("american_odds"),
                row.get("decimal_odds"),
                row.get("raw_implied_probability"),
                row.get("observed_at"),
                row.get("ingested_at"),
                row.get("scheduled_tipoff"),
                row.get("cutoff_at"),
                row.get("source_version"),
                row.get("market_key"),
                1 if row.get("is_alternate") else 0,
                row.get("raw_sha256"),
            )
            connection.execute(insert_sql, values)
        inserted = connection.total_changes - before

    return {"inserted": inserted, "skipped": len(rows) - inserted}


def fetch_snapshots(
    path: str | Path,
    *,
    source_event_id: int | None = None,
) -> list[dict[str, Any]]:
    initialize_database(path)
    query = "SELECT * FROM odds_snapshots"
    parameters: tuple[Any, ...] = ()
    if source_event_id is not None:
        query += " WHERE source_event_id = ?"
        parameters = (source_event_id,)
    query += " ORDER BY observed_at, source_event_id, market_type, participant_name"
    with connect_database(path) as connection:
        return [dict(row) for row in connection.execute(query, parameters)]


def export_json(path: str | Path, output: str | Path) -> int:
    rows = fetch_snapshots(path)
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return len(rows)


def export_csv(path: str | Path, output: str | Path) -> int:
    rows = fetch_snapshots(path)
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        output_path.write_text("", encoding="utf-8")
        return 0
    with output_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)
