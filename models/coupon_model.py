from models.domains import Coupon, CouponMatch, SoccerMatch
from mvc import Model

# Klass för att hantera data om tipskuponger.


class CouponModel(Model):
    def __init__(self, database):
        super().__init__()
        self.database = database
        self.current_coupon = None

    # Funktion som returnerar alla säsonger som har lagts till i databasen.
    def get_all_seasons(self):
        return self.database.get_all_seasons()

    # Funktion för att lägga till en ny tipskupong i databasen.
    def _create_coupon(self, row):
        if row is None:
            return None

        coupon_id, year, week = row

        return Coupon(
            coupon_id,
            year,
            week,
            []
        )

    # Funktion som returnerar alla tipskuponger, som finns tillagda i databasen.
    def get_all(self):
        rows = self.database.get_all_coupons()

        coupons = []

        for coupon_id, year, week in rows:
            coupons.append(
                Coupon(
                    coupon_id,
                    year,
                    week
                )
            )

        return coupons

    # Funktion som returnerar en viss tipskupong och matcher med hjälp av tipskupongens id.
    def get(self, coupon_id):
        row = self.database.get_coupon(coupon_id)

        if row is None:
            return None

        coupon = Coupon(*row)
        coupon.soccer_matches = self.get_coupon_matches(coupon.id)

        return coupon

    # Funktion som returnerar en viss tipskupong och matcher med hjälp av år och månad.
    def get_by_year_week(self, year, week):
        row = self.database.get_coupon_by_year_week(year, week)

        if row is None:
            return None

        coupon = Coupon(*row)
        coupon.soccer_matches = self.get_coupon_matches(coupon.id)

        return coupon

    # Funktion som returnerar alla matcher för en angiven tipskpong.
    def get_coupon_matches(self, coupon_id):
        rows = self.database.get_coupon_matches(coupon_id)
        coupon_matches = []

        for row in rows:
            (
                match_number,
                match_id,
                season_id,
                home_team,
                away_team,
                home_score,
                away_score
            ) = row

            soccer_match = SoccerMatch(
                id=match_id,
                season_id=season_id,
                home_team=home_team,
                away_team=away_team,
                match_date=None,
                home_score=home_score,
                away_score=away_score
            )

            coupon_matches.append(
                CouponMatch(
                    match_number,
                    soccer_match
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

    def get_teams(self, season_id):
        return self.database.get_teams(season_id)
