PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS raw_imports (
    import_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    observed_at TEXT NOT NULL,
    ingested_at TEXT NOT NULL,
    raw_sha256 TEXT NOT NULL,
    matchup_count INTEGER NOT NULL,
    market_count INTEGER NOT NULL,
    normalized_row_count INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'accepted',
    note TEXT,
    UNIQUE (raw_sha256, observed_at)
);

CREATE TABLE IF NOT EXISTS odds_snapshots (
    snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    import_id INTEGER NOT NULL,
    source TEXT NOT NULL,
    league TEXT,
    sport TEXT,
    source_event_id INTEGER NOT NULL,
    market_name TEXT,
    market_type TEXT NOT NULL,
    period INTEGER NOT NULL DEFAULT 0,
    side TEXT NOT NULL DEFAULT '',
    participant_id INTEGER NOT NULL DEFAULT -1,
    participant_name TEXT NOT NULL,
    line REAL NOT NULL DEFAULT -999999.0,
    american_odds INTEGER NOT NULL,
    decimal_odds REAL NOT NULL,
    raw_implied_probability REAL NOT NULL,
    observed_at TEXT NOT NULL,
    ingested_at TEXT NOT NULL,
    scheduled_tipoff TEXT,
    cutoff_at TEXT,
    source_version INTEGER,
    market_key TEXT,
    is_alternate INTEGER NOT NULL DEFAULT 0 CHECK (is_alternate IN (0, 1)),
    raw_sha256 TEXT NOT NULL,
    FOREIGN KEY (import_id) REFERENCES raw_imports(import_id) ON DELETE CASCADE,
    UNIQUE (
        source,
        source_event_id,
        market_type,
        period,
        side,
        participant_id,
        line,
        american_odds,
        observed_at
    )
);

CREATE INDEX IF NOT EXISTS idx_odds_event_time
ON odds_snapshots (source_event_id, observed_at);

CREATE INDEX IF NOT EXISTS idx_odds_participant_time
ON odds_snapshots (participant_id, observed_at);

CREATE INDEX IF NOT EXISTS idx_odds_market_lookup
ON odds_snapshots (league, market_type, period, observed_at);
