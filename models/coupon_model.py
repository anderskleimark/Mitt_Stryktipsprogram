from models.domains import (Competition, Coupon, CouponMatch, Season,
                            SoccerMatch, Team)
from mvc import Model

# Klass för att hantera data om tipskuponger.


class CouponModel(Model):
    def __init__(self, database):
        super().__init__()
        self.database = database
        self.current_coupon = None

    # Funktion som returnerar alla säsonger som har lagts till i databasen.
    def get_all_seasons(self):
        rows = self.database.get_all_seasons()
        seasons = []

        for row in rows:
            seasons.append(
                Season(
                    id=row["id"],
                    competition=Competition(
                        id=row["competition_id"],
                        name=row["name"],
                        country=row["country"]
                    ),
                    start_year=row["start_year"],
                    end_year=row["end_year"]
                )
            )

        return seasons

    # Funktion för att lägga till en ny tipskupong i databasen.
    def _create_coupon(self, row):
        if row is None:
            return None

        coupon_id, year, week = row

        return Coupon(
            id=coupon_id,
            year=year,
            week=week,
            soccer_matches=[]
        )

    # Funktion som returnerar alla tipskuponger, som finns tillagda i databasen.
    def get_all(self):
        rows = self.database.get_all_coupons()

        coupons = []

        for coupon_id, year, week in rows:
            coupons.append(
                Coupon(
                    id=coupon_id,
                    year=year,
                    week=week
                )
            )

        return coupons

    # Funktion som returnerar en viss tipskupong och matcher med hjälp av tipskupongens id.
    def get(self, coupon_id):
        row = self.database.get_coupon(coupon_id)
        if row is None:
            return None

        coupon = Coupon(
            id=row["id"],
            year=row["year"],
            week=row["week"]
        )
        coupon.soccer_matches = self.get_coupon_matches(coupon.id)
        return coupon

    # Funktion som returnerar en viss tipskupong och matcher med hjälp av år och månad.
    def get_by_year_week(self, year, week):
        row = self.database.get_coupon_by_year_week(year, week)

        if row is None:
            return None

        coupon = Coupon(
            id=row["id"],
            year=row["year"],
            week=row["week"]
        )
        coupon.soccer_matches = self.get_coupon_matches(coupon.id)
        return coupon

    # Funktion som returnerar alla matcher för en angiven tipskpong.
    def get_coupon_matches(self, coupon_id):
        rows = self.database.get_coupon_matches(coupon_id)
        coupon_matches = []

        for row in rows:
            coupon_matches.append(
                CouponMatch(
                    number=row["match_number"],
                    soccer_match=SoccerMatch(
                        id=row["match_id"],
                        season_id=row["season_id"],
                        competition=Competition(
                            id=row["competition_id"],
                            name=row["competition_name"],
                            country=row["country"]
                        ),
                        home_team=Team(
                            id=row["home_team_id"],
                            name=row["home_team_name"]
                        ),
                        away_team=Team(
                            id=row["away_team_id"],
                            name=row["away_team_name"]
                        ),
                        match_date=None,
                        home_score=row["home_score"],
                        away_score=row["away_score"]
                    )
                )
            )

        return coupon_matches

    # Funktion för att lägga till en fullständig tipskupong med hemmalag
    # och bortalag för de tretton matcherna.
    def create_coupon_with_matches(self, year, week, coupon_matches):
        coupon_id = self.database.create_coupon(year, week)

        for coupon_match in coupon_matches:
            match = coupon_match.soccer_match

            if not match.home_team.strip():
                raise ValueError(
                    f"Hemmalag saknas i match {coupon_match.number}"
                )

            if not match.away_team.strip():
                raise ValueError(
                    f"Bortalag saknas i match {coupon_match.number}"
                )

            # Skapa eller hämta hemmalag
            home_team_id = self.database.get_team_id(
                match.home_team
            )

            # Skapa eller hämta bortalag
            away_team_id = self.database.get_team_id(
                match.away_team
            )

            # Lägg till fotbollsmatchen.
            match_id = self.database.add_match(
                match.season_id,
                home_team_id,
                away_team_id
            )

            # Lägg till matchen till tipskupongen.
            self.database.add_coupon_match(
                coupon_id,
                coupon_match.number,
                match_id
            )

        return coupon_id

    # Funktion som uppdaterar databasen med ett matchresultat.
    def update_match_score(self, coupon_id, match_number, home_score, away_score):
        self.database.update_match_score(
            coupon_id,
            match_number,
            home_score,
            away_score
        )

    # Funktion som hämtar alla lag för en viss säsong.
    def get_teams(self, season_id):
        return self.database.get_teams(season_id)

    # Funktion som hämtar tävlingen via säsongen.
    def get_competition_by_season(self, season_id):
        row = self.database.get_competition_by_season(season_id)

        if row is None:
            return None

        return Competition(
            id=row["id"],
            name=row["name"],
            country=row["country"]
        )
