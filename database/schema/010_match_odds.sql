CREATE TABLE IF NOT EXISTS match_odds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    match_id INTEGER NOT NULL UNIQUE,

    -- Bet365
    bet365_home REAL,
    bet365_draw REAL,
    bet365_away REAL,

    -- Högsta rapporterade marknadsodds
    max_home REAL,
    max_draw REAL,
    max_away REAL,

    -- Genomsnittliga marknadsodds
    average_home REAL,
    average_draw REAL,
    average_away REAL,

    -- Bet365 closing odds
    bet365_closing_home REAL,
    bet365_closing_draw REAL,
    bet365_closing_away REAL,

    -- Högsta rapporterade closing odds
    max_closing_home REAL,
    max_closing_draw REAL,
    max_closing_away REAL,

    -- Genomsnittliga closing odds
    average_closing_home REAL,
    average_closing_draw REAL,
    average_closing_away REAL,

    -- Datakälla
    source TEXT,

    FOREIGN KEY(match_id)
    REFERENCES matches(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);