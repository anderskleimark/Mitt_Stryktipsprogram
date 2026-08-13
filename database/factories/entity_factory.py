from datetime import date
from models.domains import (Bet, BetDetails, Competition, Country, Coupon,
                            CouponMatch, Season, SoccerMatch, System,
                            Team)


class EntityFactory:
    """
        Fabrik som skapar domänobjekt från databasrader.
    """

    def create_bet(self, row):
        """
            Skapar och returnerar ett spel.
        """
        return Bet(
            id=row["bet_id"],
            bet_date=row["bet_date"],
            correct_count=row["correct_count"],
            prize=row["prize"],
            # total_cost=row["total_cost"],
            system=self.create_system(row),
            coupon=self.create_coupon(row)
        )

    def create_bet_details(self, row):
        """
            Skapar och returnerar detaljer för ett spel.
        """
        return BetDetails(
            bet=self.create_bet(row),
            match_number=row["bet_details_match_number"],
            frame_value=row["bet_details_frame_value"],
            key_value=row["bet_details_key_value"],
            mathematical_value=row["bet_details_mathematical_value"]
        )

    def create_country(self, row, prefix=""):
        """
            Skapar och returnerar ett land.
            Prefix används när flera länder finns i samma databasrad,
            exempelvis hemma- och bortalag.
        """
        return Country(
            id=row[f"{prefix}country_id"],
            country_name=row[f"{prefix}country_name"],
            iso_code=row[f"{prefix}country_code"]
        )

    def create_coupon(self, row):
        """
            Skapar och returnerar en stryktipskupong.
        """
        return Coupon(
            id=row["coupon_id"],
            coupon_year=row["coupon_year"],
            coupon_week=row["coupon_week"],
            soccer_matches=[]
        )

    def create_coupon_match(self, row):
        """
            Skapar en match kopplad till en kupong.
        """
        return CouponMatch(
            match_number=row["coupon_match_number"],
            soccer_match=self.create_soccer_match(row)
        )

    def create_competition(self, row, prefix=""):
        """
            Skapar och returnerar en tävling eller liga.

            Prefix används när tävlingen ingår i en större databasrad,
            exempelvis en fotbollsmatch.
        """
        return Competition(
            id=row[f"{prefix}competition_id"],
            competition_name=row[f"{prefix}competition_name"],
            country=self.create_country(
                row,
                f"{prefix}competition_"
            )
        )

    def create_season(self, row, prefix=""):
        """
            Skapar och returnerar en säsong.
            Prefix används när säsongen ingår i en större databasrad.
        """
        return Season(
            id=row[f"{prefix}season_id"],
            competition=self.create_competition(
                row,
                prefix
            ),
            start_year=row[f"{prefix}season_start_year"],
            end_year=row[f"{prefix}season_end_year"]
        )

    def create_soccer_match(self, row):
        """
            Skapar och returnerar en fotbollsmatch.
        """
        return SoccerMatch(
            id=row["soccer_match_id"],
            season=self.create_season(
                row,
                "soccer_match_"
            ),
            home_team=self.create_team(
                row,
                "soccer_match_home_"
            ),
            away_team=self.create_team(
                row,
                "soccer_match_away_"
            ),
            match_date=date.fromisoformat(
                row["soccer_match_date"]
            ),
            home_score=row["soccer_match_home_score"],
            away_score=row["soccer_match_away_score"]
        )

    def create_system(self, row):
        """
            Skapar och returnerar ett system.
        """
        return System(
            id=row["system_id"],
            system_type=row["system_type"],
            full_covers=row["full_covers"],
            half_covers=row["half_covers"],
            row_count=row["row_count"]
        )

    def create_team(self, row, prefix=""):
        """
            Skapar och returnerar ett lag.

            Prefix används när flera lag finns i samma databasrad,
            exempelvis hemma- och bortalag i en match.
        """
        return Team(
            id=row[f"{prefix}team_id"],
            country=self.create_country(row, f"{prefix}team_"),
            team_name=row[f"{prefix}team_name"],
            display_name=row[f"{prefix}team_display_name"]
        )
