from mvc import Model

# Klass för att hantera matcher.


class Game:

    def __init__(
        self,
        number,
        home_team,
        away_team,
        home_score=None,
        away_score=None,
    ):
        self.number = number
        self.home_team = home_team
        self.away_team = away_team
        self.home_score = home_score
        self.away_score = away_score

    @property
    def result_1x2(self):
        if self.home_score is None or self.away_score is None:
            return "-"
        elif self.home_score > self.away_score:
            return "1"
        elif self.home_score == self.away_score:
            return "X"
        else:
            return "2"


# En specifik Kupong-klass för att hantera kuponger som objekt.

class Coupon:
    def __init__(self, id, year, week, games):
        self.id = id
        self.year = year
        self.week = week
        self.games = games

# Klass för att hantera data om tipskuponger.


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

        rows = self.database.get_matches(coupon_id)

        games = []

        for number, home_team, away_team in rows:
            games.append(
                Game(
                    number,
                    home_team,
                    away_team
                )
            )

        return Coupon(
            coupon_id,
            year,
            week,
            games
        )

    # Funktion för att lägga till en fullständig tipskupong med hemmalag och bortalag för de tretton matcherna.
    def create_coupon_with_games(self, year, week, games):
        for game_number, home_team, away_team in matches:

            if not home_team.strip():
                raise ValueError(
                    f"Hemmalag saknas i match {game_number}"
                )

            if not away_team.strip():
                raise ValueError(
                    f"Bortalag saknas i match {game_number}"
                )

        coupon_id = self.database.create_coupon(
            year,
            week
        )

        for game_number, home_team, away_team in games:
            self.database.add_match(
                coupon_id,
                game_number,
                home_team,
                away_team
            )

        return coupon_id
