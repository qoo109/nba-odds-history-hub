"""SQLite persistence, registries, and history-aware deduplication."""
from __future__ import annotations

import csv
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "sql" / "schema.sql"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect_database(path: str | Path) -> sqlite3.Connection:
    db_path = Path(path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _table_columns(connection: sqlite3.Connection, table: str) -> set[str]:
    return {str(row["name"]) for row in connection.execute(f"PRAGMA table_info({table})")}


def _ensure_column(connection: sqlite3.Connection, table: str, definition: str) -> None:
    name = definition.split()[0]
    if name not in _table_columns(connection, table):
        connection.execute(f"ALTER TABLE {table} ADD COLUMN {definition}")


def initialize_database(
    path: str | Path, *, schema_path: str | Path = DEFAULT_SCHEMA_PATH
) -> None:
    schema = Path(schema_path).read_text(encoding="utf-8")
    with connect_database(path) as connection:
        # Add columns before executing new indexes so V0.2 databases migrate safely.
        table_exists = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='odds_snapshots'"
        ).fetchone()
        if table_exists:
            _ensure_column(connection, "odds_snapshots", "bookmaker_id TEXT NOT NULL DEFAULT 'unknown'")
            _ensure_column(connection, "odds_snapshots", "canonical_event_id TEXT")
        connection.executescript(schema)
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_odds_quote_history
            ON odds_snapshots (
                source, bookmaker_id, source_event_id, market_type, period, side,
                participant_id, is_alternate, observed_at
            )
            """
        )


def register_source(
    path: str | Path,
    *,
    source_id: str,
    display_name: str,
    source_class: str = "manual_capture",
    access_mode: str = "manual",
    usage_boundary: str | None = None,
) -> None:
    initialize_database(path)
    with connect_database(path) as connection:
        connection.execute(
            """
            INSERT INTO data_sources (
                source_id, display_name, source_class, access_mode, usage_boundary, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(source_id) DO UPDATE SET
                display_name=excluded.display_name,
                source_class=excluded.source_class,
                access_mode=excluded.access_mode,
                usage_boundary=excluded.usage_boundary
            """,
            (source_id, display_name, source_class, access_mode, usage_boundary, _utc_now_iso()),
        )


def register_bookmaker(
    path: str | Path,
    *,
    bookmaker_id: str,
    display_name: str,
    source_id: str | None = None,
    active: bool = True,
) -> None:
    initialize_database(path)
    with connect_database(path) as connection:
        connection.execute(
            """
            INSERT INTO bookmakers (bookmaker_id, display_name, source_id, active, created_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(bookmaker_id) DO UPDATE SET
                display_name=excluded.display_name,
                source_id=excluded.source_id,
                active=excluded.active
            """,
            (bookmaker_id, display_name, source_id, 1 if active else 0, _utc_now_iso()),
        )


def register_source_events(path: str | Path, rows: list[dict[str, Any]]) -> int:
    """Create source-event placeholders without inventing canonical NBA IDs."""
    initialize_database(path)
    unique: dict[tuple[str, int], dict[str, Any]] = {}
    for row in rows:
        source = str(row["source"])
        source_event_id = int(row["source_event_id"])
        unique[(source, source_event_id)] = row
    with connect_database(path) as connection:
        for (source, source_event_id), row in unique.items():
            connection.execute(
                """
                INSERT INTO source_events (
                    source_id, source_event_id, bookmaker_id, league, event_type,
                    title, scheduled_tipoff, cutoff_at, canonical_event_id,
                    mapping_status, first_observed_at, last_observed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'unmapped', ?, ?)
                ON CONFLICT(source_id, source_event_id) DO UPDATE SET
                    bookmaker_id=excluded.bookmaker_id,
                    league=COALESCE(excluded.league, source_events.league),
                    event_type=COALESCE(excluded.event_type, source_events.event_type),
                    title=COALESCE(excluded.title, source_events.title),
                    scheduled_tipoff=COALESCE(excluded.scheduled_tipoff, source_events.scheduled_tipoff),
                    cutoff_at=COALESCE(excluded.cutoff_at, source_events.cutoff_at),
                    last_observed_at=MAX(source_events.last_observed_at, excluded.last_observed_at)
                """,
                (
                    source,
                    source_event_id,
                    row.get("bookmaker_id"),
                    row.get("league"),
                    row.get("event_type") or "market",
                    row.get("market_name"),
                    row.get("scheduled_tipoff"),
                    row.get("cutoff_at"),
                    row.get("canonical_event_id"),
                    row.get("observed_at"),
                    row.get("observed_at"),
                ),
            )
    return len(unique)


def upsert_canonical_event(
    path: str | Path,
    *,
    canonical_event_id: str,
    league: str,
    event_type: str,
    title: str | None = None,
    scheduled_tipoff: str | None = None,
    home_team: str | None = None,
    away_team: str | None = None,
) -> None:
    initialize_database(path)
    with connect_database(path) as connection:
        connection.execute(
            """
            INSERT INTO canonical_events (
                canonical_event_id, league, event_type, title, scheduled_tipoff,
                home_team, away_team, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(canonical_event_id) DO UPDATE SET
                league=excluded.league,
                event_type=excluded.event_type,
                title=excluded.title,
                scheduled_tipoff=excluded.scheduled_tipoff,
                home_team=excluded.home_team,
                away_team=excluded.away_team
            """,
            (
                canonical_event_id, league, event_type, title, scheduled_tipoff,
                home_team, away_team, _utc_now_iso(),
            ),
        )


def map_source_event(
    path: str | Path,
    *,
    source_id: str,
    source_event_id: int,
    canonical_event_id: str,
) -> None:
    initialize_database(path)
    with connect_database(path) as connection:
        updated = connection.execute(
            """
            UPDATE source_events
            SET canonical_event_id = ?, mapping_status = 'mapped'
            WHERE source_id = ? AND source_event_id = ?
            """,
            (canonical_event_id, source_id, source_event_id),
        ).rowcount
        if updated != 1:
            raise KeyError(f"Unknown source event: {source_id}/{source_event_id}")
        connection.execute(
            """
            UPDATE odds_snapshots SET canonical_event_id = ?
            WHERE source = ? AND source_event_id = ?
            """,
            (canonical_event_id, source_id, source_event_id),
        )


def _stored_line(value: Any) -> float:
    return float(value) if value is not None else -999999.0


def _quote_identity(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        row.get("source"),
        row.get("bookmaker_id") or "unknown",
        row.get("source_event_id"),
        row.get("market_type"),
        int(row.get("period") or 0),
        row.get("side") or "",
        row.get("participant_id") if row.get("participant_id") is not None else -1,
        1 if row.get("is_alternate") else 0,
    )


def _latest_quote(connection: sqlite3.Connection, row: dict[str, Any]) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT line, american_odds FROM odds_snapshots
        WHERE source = ? AND bookmaker_id = ? AND source_event_id = ?
          AND market_type = ? AND period = ? AND side = ?
          AND participant_id = ? AND is_alternate = ?
          AND julianday(observed_at) < julianday(?)
        ORDER BY julianday(observed_at) DESC, snapshot_id DESC LIMIT 1
        """,
        _quote_identity(row) + (row.get("observed_at"),),
    ).fetchone()


def insert_snapshot_rows_detailed(
    path: str | Path,
    rows: list[dict[str, Any]],
    *,
    matchup_count: int,
    market_count: int,
    note: str | None = None,
    dedupe_mode: str = "exact",
) -> dict[str, int | str]:
    """Insert rows using exact or price-change-only history retention."""
    if not rows:
        raise ValueError("rows cannot be empty")
    if dedupe_mode not in {"exact", "changes-only"}:
        raise ValueError("dedupe_mode must be 'exact' or 'changes-only'")

    initialize_database(path)
    first = rows[0]
    columns = [
        "import_id", "source", "bookmaker_id", "canonical_event_id", "league", "sport",
        "source_event_id", "market_name", "market_type", "period", "side",
        "participant_id", "participant_name", "line", "american_odds", "decimal_odds",
        "raw_implied_probability", "observed_at", "ingested_at", "scheduled_tipoff",
        "cutoff_at", "source_version", "market_key", "is_alternate", "raw_sha256",
    ]
    placeholders = ", ".join("?" for _ in columns)
    insert_sql = f"INSERT OR IGNORE INTO odds_snapshots ({', '.join(columns)}) VALUES ({placeholders})"

    with connect_database(path) as connection:
        connection.execute(
            """
            INSERT OR IGNORE INTO raw_imports (
                source, observed_at, ingested_at, raw_sha256,
                matchup_count, market_count, normalized_row_count, note
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                first["source"], first["observed_at"], first["ingested_at"],
                first["raw_sha256"], matchup_count, market_count, len(rows), note,
            ),
        )
        import_row = connection.execute(
            "SELECT import_id FROM raw_imports WHERE raw_sha256 = ? AND observed_at = ?",
            (first["raw_sha256"], first["observed_at"]),
        ).fetchone()
        if import_row is None:
            raise RuntimeError("Failed to create or locate raw import record")
        import_id = int(import_row["import_id"])

        inserted = 0
        unchanged_skipped = 0
        exact_duplicate_skipped = 0
        for row in rows:
            if dedupe_mode == "changes-only":
                latest = _latest_quote(connection, row)
                if (
                    latest is not None
                    and float(latest["line"]) == _stored_line(row.get("line"))
                    and int(latest["american_odds"]) == int(row["american_odds"])
                ):
                    unchanged_skipped += 1
                    continue
            values = (
                import_id, row.get("source"), row.get("bookmaker_id") or "unknown",
                row.get("canonical_event_id"), row.get("league"), row.get("sport"),
                row.get("source_event_id"), row.get("market_name"), row.get("market_type"),
                int(row.get("period") or 0), row.get("side") or "",
                row.get("participant_id") if row.get("participant_id") is not None else -1,
                row.get("participant_name") or "unknown", _stored_line(row.get("line")),
                row.get("american_odds"), row.get("decimal_odds"),
                row.get("raw_implied_probability"), row.get("observed_at"),
                row.get("ingested_at"), row.get("scheduled_tipoff"), row.get("cutoff_at"),
                row.get("source_version"), row.get("market_key"),
                1 if row.get("is_alternate") else 0, row.get("raw_sha256"),
            )
            before = connection.total_changes
            connection.execute(insert_sql, values)
            if connection.total_changes > before:
                inserted += 1
            else:
                exact_duplicate_skipped += 1

    return {
        "mode": dedupe_mode,
        "inserted": inserted,
        "skipped": len(rows) - inserted,
        "unchanged_skipped": unchanged_skipped,
        "exact_duplicate_skipped": exact_duplicate_skipped,
    }


def insert_snapshot_rows(
    path: str | Path,
    rows: list[dict[str, Any]],
    *,
    matchup_count: int,
    market_count: int,
    note: str | None = None,
) -> dict[str, int]:
    result = insert_snapshot_rows_detailed(
        path, rows, matchup_count=matchup_count, market_count=market_count,
        note=note, dedupe_mode="exact",
    )
    return {"inserted": int(result["inserted"]), "skipped": int(result["skipped"])}


def fetch_snapshots(path: str | Path, *, source_event_id: int | None = None) -> list[dict[str, Any]]:
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
    output_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
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
