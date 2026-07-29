CREATE TABLE IF NOT EXISTS systems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    system_type TEXT NOT NULL,
    full_covers INTEGER NOT NULL,
    half_covers INTEGER NOT NULL,
    row_count INTEGER NOT NULL,
    UNIQUE(system_type, full_covers, half_covers, row_count)
);