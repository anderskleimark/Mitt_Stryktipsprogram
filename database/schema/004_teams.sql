CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    country_id INTEGER NOT NULL,
    team_name TEXT NOT NULL,
    display_name TEXT NOT NULL,
    FOREIGN KEY(country_id)
    REFERENCES countries(id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT,
    UNIQUE(country_id, team_name)
);