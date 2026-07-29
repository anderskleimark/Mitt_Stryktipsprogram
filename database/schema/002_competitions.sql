CREATE TABLE IF NOT EXISTS competitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    competition_name TEXT NOT NULL,
    country_id INTEGER NOT NULL,
    FOREIGN KEY(country_id)
    REFERENCES countries(id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT,
    UNIQUE(country_id, competition_name)
);