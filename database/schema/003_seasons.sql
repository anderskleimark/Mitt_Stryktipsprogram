CREATE TABLE IF NOT EXISTS seasons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    competition_id INTEGER NOT NULL,
    start_year INTEGER NOT NULL,
    end_year INTEGER NOT NULL,
    FOREIGN KEY(competition_id)
    REFERENCES competitions(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
    UNIQUE(competition_id, start_year, end_year)
);

CREATE TABLE IF NOT EXISTS season_teams (
    season_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    PRIMARY KEY(season_id, team_id),

    FOREIGN KEY(season_id)
    REFERENCES seasons(id)
    ON DELETE CASCADE,

    FOREIGN KEY(team_id)
    REFERENCES teams(id)
    ON DELETE CASCADE
)