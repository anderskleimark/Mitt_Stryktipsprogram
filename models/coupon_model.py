class CouponModel:

    def __init__(self, database):
        self.database = database

    def create_coupon(self, year, week):
        self.database.create_coupon(year, week)

    def get_coupon(self, year, week):
        return self.database.get_coupon(year, week)
