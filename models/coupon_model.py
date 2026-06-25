from mvc import Model

# Klass för att hantera data om tipskuponger.


class Coupon:
    def __init__(self, id, year, week, matches):
        self.id = id
        self.year = year
        self.week = week
        self.matches = matches


class CouponModel(Model):
    def __init__(self, database):
        super().__init__()
        self.database = database

    # Funktion för att lägga till en ny tipskupong i databasen.
    def create_coupon(self, year, week):
        self.database.create_coupon(year, week)

    # Funktion som returnerar en viss tipskupong och matcher med hjälp av år och månad.
    def get_coupon(self, year, week):
        data = self.database.get_coupon(year, week)

        if data is None:
            return None

        coupon_id, year, week = data
        matches = self.database.get_matches(coupon_id)
        return Coupon(coupon_id, year, week, matches)

    # Funktion för att lägga till en fullständig tipskupong med hemmalag och bortalag för de tretton matcherna.
    def create_coupon_with_matches(self, year, week, matches):
        for match_number, home_team, away_team in matches:

            if not home_team.strip():
                raise ValueError(
                    f"Hemmalag saknas i match {match_number}"
                )

            if not away_team.strip():
                raise ValueError(
                    f"Bortalag saknas i match {match_number}"
                )

        coupon_id = self.database.create_coupon(
            year,
            week
        )

        for match_number, home_team, away_team in matches:
            self.database.add_match(
                coupon_id,
                match_number,
                home_team,
                away_team
            )

        return coupon_id
