from models.domains import Country, Competition, Team, SoccerMatch, Season


class EntityFactory:
    def create_team(self, row):
        return Team(
            id=row["team_id"],
            country=self.create_country(row),
            team_name=row["team_name"],
            display_name=row["team_display_name"]
        )

    def create_country(self, row):
        return Country(
            id=row["country_id"],
            country_name=row["country_name"],
            iso_code=row["country_code"]
        )

    def create_competition(self, row):
        return Competition(
            id=row["competition_id"],
            competition_name=row["competition_name"],
            country=self.create_country(row)
        )

    def create_season(self, row):
        return Season(
            id=row["season_id"],
            competition=self.create_competition(row),
            start_year=row["start_year"],
            end_year=row["end_year"]
        )

    def create_match(self, row):
        return SoccerMatch(
            id=row["match_id"],
            season=self.create_season(row),
            home_team=self.create_team(row),
            away_team=self.create_team(row),
            match_date=row["match_date"],
            home_score=row["home_score"],
            away_score=row["away_score"]
        )
