from mvc import Model


class CouponModel(Model):
    def __init__(self, database):
        super().__init__()
        self.database = database
        self.current_coupon = None

    def get_all(self):
        return self.database.coupon_repository.get_all_coupons()

    def get(self, coupon_id):
        return self.database.coupon_repository.get(coupon_id)

    def get_by_year_week(self, year, week):
        return self.database.coupon_repository.get_coupon_by_year_week(
            year,
            week
        )

    def delete(self, coupon_id):
        self.database.coupon_repository.delete_coupon(coupon_id)

    def get_coupon_matches(self, coupon_id):
        return self.database.coupon_repository.get_coupon_matches(coupon_id)

    def add_coupon_with_matches(self, year, week, coupon_matches):
        return self.database.coupon_repository.add_coupon_with_matches(
            year,
            week,
            coupon_matches
        )

    def update_match_score(self, coupon_id, match_number, home_score, away_score):
        self.database.soccer_match_repository.update_match_score(
            coupon_id,
            match_number,
            home_score,
            away_score
        )
