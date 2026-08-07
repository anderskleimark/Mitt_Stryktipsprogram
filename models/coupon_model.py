from datetime import date

from mvc import Model


class CouponModel(Model):
    def __init__(self, database):
        super().__init__()
        self.database = database
        self.current_coupon = None

    def get_all(self):
        return self.database.coupon_repository.get_all_coupons()

    def get(self, coupon_id):
        return self.database.coupon_repository.get_coupon(coupon_id)

    def get_by_year_week(self, year, week):
        return self.database.coupon_repository.get_coupon_by_year_week(
            year,
            week
        )

    def delete(self, coupon_id):
        self.database.coupon_repository.delete_coupon(coupon_id)

    def get_coupon_matches(self, coupon_id):
        return self.database.coupon_repository.get_coupon_matches(coupon_id)

    def add_coupon_with_matches(
        self,
        year,
        week,
        coupon_matches
    ):
        """
            Skapar en kupong och sparar dess matcher.

            Matchdatum sätts till lördagen i den vecka
            som kupongen avser.
        """
        coupon_id = (
            self.database.coupon_repository.add_coupon(
                year,
                week
            )
        )

        match_date = date.fromisocalendar(
            year,
            week,
            6
        )

        for coupon_match in coupon_matches:
            match = coupon_match.soccer_match

            match.match_date = match_date

            match_id = (
                self.database.soccer_match_repository.add_match(
                    season_id=match.season.id,
                    home_team_id=match.home_team.id,
                    away_team_id=match.away_team.id,
                    match_date=match.match_date,
                    home_score=match.home_score,
                    away_score=match.away_score
                )
            )

            self.database.coupon_repository.add_coupon_match(
                coupon_id,
                coupon_match.match_number,
                match_id
            )

        return coupon_id

    def update_match_score(self, coupon_id, match_number, home_score, away_score):
        self.database.soccer_match_repository.update_match_score(
            coupon_id,
            match_number,
            home_score,
            away_score
        )
