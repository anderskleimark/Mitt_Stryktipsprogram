CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    season_id INTEGER NOT NULL,
    home_team_id INTEGER NOT NULL,
    away_team_id INTEGER NOT NULL,
    match_date TEXT NOT NULL,
    home_score INTEGER,
    away_score INTEGER,
    FOREIGN KEY(season_id)
    REFERENCES seasons(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
    FOREIGN KEY(home_team_id)
    REFERENCES teams(id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT,
    FOREIGN KEY(away_team_id)
    REFERENCES teams(id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT,
    UNIQUE(season_id, match_date, home_team_id, away_team_id)
);