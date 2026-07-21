PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS data_sources (
    source_id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    source_class TEXT NOT NULL DEFAULT 'manual_capture',
    access_mode TEXT NOT NULL DEFAULT 'manual',
    usage_boundary TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS bookmakers (
    bookmaker_id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    source_id TEXT,
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
    created_at TEXT NOT NULL,
    FOREIGN KEY (source_id) REFERENCES data_sources(source_id)
);

CREATE TABLE IF NOT EXISTS canonical_events (
    canonical_event_id TEXT PRIMARY KEY,
    league TEXT NOT NULL,
    event_type TEXT NOT NULL,
    title TEXT,
    scheduled_tipoff TEXT,
    home_team TEXT,
    away_team TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS source_events (
    source_id TEXT NOT NULL,
    source_event_id INTEGER NOT NULL,
    bookmaker_id TEXT,
    league TEXT,
    event_type TEXT,
    title TEXT,
    scheduled_tipoff TEXT,
    cutoff_at TEXT,
    canonical_event_id TEXT,
    mapping_status TEXT NOT NULL DEFAULT 'unmapped',
    first_observed_at TEXT NOT NULL,
    last_observed_at TEXT NOT NULL,
    PRIMARY KEY (source_id, source_event_id),
    FOREIGN KEY (source_id) REFERENCES data_sources(source_id),
    FOREIGN KEY (bookmaker_id) REFERENCES bookmakers(bookmaker_id),
    FOREIGN KEY (canonical_event_id) REFERENCES canonical_events(canonical_event_id)
);

CREATE TABLE IF NOT EXISTS source_event_schedule_versions (
    schedule_version_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT NOT NULL,
    source_event_id INTEGER NOT NULL,
    version_number INTEGER NOT NULL CHECK (version_number >= 1),
    scheduled_tipoff TEXT NOT NULL,
    home_team_abbr TEXT NOT NULL,
    away_team_abbr TEXT NOT NULL,
    mapping_status TEXT NOT NULL DEFAULT 'unmapped' CHECK (
        mapping_status IN (
            'unmapped', 'candidate_unverified', 'verified',
            'rejected', 'quarantined', 'mapped'
        )
    ),
    mapping_method TEXT NOT NULL DEFAULT 'none',
    observed_at TEXT NOT NULL,
    source_payload_sha256 TEXT NOT NULL,
    is_current INTEGER NOT NULL DEFAULT 1 CHECK (is_current IN (0, 1)),
    created_at TEXT NOT NULL,
    UNIQUE (source_id, source_event_id, version_number),
    FOREIGN KEY (source_id, source_event_id)
        REFERENCES source_events(source_id, source_event_id)
        ON DELETE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_schedule_one_current_version
ON source_event_schedule_versions (source_id, source_event_id)
WHERE is_current = 1;

CREATE INDEX IF NOT EXISTS idx_schedule_tipoff
ON source_event_schedule_versions (scheduled_tipoff, is_current);

CREATE TABLE IF NOT EXISTS source_event_mapping_audit (
    mapping_audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT NOT NULL,
    source_event_id INTEGER NOT NULL,
    canonical_event_id TEXT,
    previous_status TEXT NOT NULL,
    new_status TEXT NOT NULL CHECK (
        new_status IN (
            'unmapped', 'candidate_unverified', 'verified',
            'rejected', 'quarantined', 'mapped'
        )
    ),
    mapping_method TEXT NOT NULL,
    reason_code TEXT NOT NULL,
    actor_type TEXT NOT NULL,
    decided_at TEXT NOT NULL,
    source_payload_sha256 TEXT,
    note TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (source_id, source_event_id)
        REFERENCES source_events(source_id, source_event_id)
        ON DELETE CASCADE,
    FOREIGN KEY (canonical_event_id)
        REFERENCES canonical_events(canonical_event_id)
);

CREATE INDEX IF NOT EXISTS idx_mapping_audit_event_time
ON source_event_mapping_audit (source_id, source_event_id, decided_at);

CREATE VIEW IF NOT EXISTS current_source_event_schedules AS
SELECT
    source_id,
    source_event_id,
    version_number,
    scheduled_tipoff,
    home_team_abbr,
    away_team_abbr,
    mapping_status,
    mapping_method,
    observed_at,
    source_payload_sha256
FROM source_event_schedule_versions
WHERE is_current = 1;

CREATE VIEW IF NOT EXISTS source_event_mapping_status_summary AS
SELECT mapping_status, COUNT(*) AS event_count
FROM source_events
GROUP BY mapping_status;

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
    bookmaker_id TEXT NOT NULL DEFAULT 'unknown',
    canonical_event_id TEXT,
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
        source, bookmaker_id, source_event_id, market_type, period, side,
        participant_id, line, american_odds, observed_at
    )
);

CREATE INDEX IF NOT EXISTS idx_odds_event_time
ON odds_snapshots (source_event_id, observed_at);
CREATE INDEX IF NOT EXISTS idx_odds_participant_time
ON odds_snapshots (participant_id, observed_at);
CREATE INDEX IF NOT EXISTS idx_odds_market_lookup
ON odds_snapshots (league, market_type, period, observed_at);
