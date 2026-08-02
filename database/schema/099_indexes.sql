CREATE INDEX IF NOT EXISTS idx_matches_season
ON matches(season_id);
    
CREATE INDEX IF NOT EXISTS idx_matches_home_team
ON matches(home_team_id);
    
CREATE INDEX IF NOT EXISTS idx_matches_away_team
ON matches(away_team_id);
    
CREATE INDEX IF NOT EXISTS idx_season_teams_team
ON season_teams(team_id);