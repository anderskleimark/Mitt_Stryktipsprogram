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
            return ""
        elif self.home_score > self.away_score:
            return "1"
        elif self.home_score == self.away_score:
            return "X"
        else:
            return "2"


# En specifik Kupong-klass för att hantera kuponger som objekt.

class Coupon:
    def __init__(self, id, year, week, games=None):
        self.id = id
        self.year = year
        self.week = week
        self.games = games

# Klass för att hantera data om tipskuponger.


class CouponModel(Model):
    def __init__(self, database):
        super().__init__()
        self.database = database
        self.current_coupon = None

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

    # Funktion som returnerar en viss tipskupong och matcher med hjälp av år och månad.

    def get(self, coupon_id):

        return self._create_coupon(
            self.database.get_coupon(coupon_id)
        )

    def get_by_year_week(self, year, week):

        return self._create_coupon(
            self.database.get_coupon_by_year_week(
                year,
                week
            )
        )

    def get_games(self, coupon_id):

        rows = self.database.get_games(coupon_id)

        games = []

        for row in rows:

            (
                game_number,
                home_team,
                away_team,
                home_score,
                away_score
            ) = row

            games.append(
                Game(
                    game_number,
                    home_team,
                    away_team,
                    home_score,
                    away_score
                )
            )

        return games

    # Funktion för att lägga till en fullständig tipskupong med hemmalag och bortalag för de tretton matcherna.
    def create_coupon_with_games(self, year, week, games):
        # Validering
        for game in games:

            if not game.home_team.strip():
                raise ValueError(
                    f"Hemmalag saknas i match {game.number}"
                )

            if not game.away_team.strip():
                raise ValueError(
                    f"Bortalag saknas i match {game.number}"
                )

        coupon_id = self.database.create_coupon(year, week)

        for game in games:
            self.database.add_game(
                coupon_id,
                game.number,
                game.home_team,
                game.away_team
            )

        return coupon_id

    # Funktion som uppdaterar databasen med ett matchresultat.
    def update_game_score(self, coupon_id, game_number, home_score, away_score):

        self.database.update_game_score(
            coupon_id,
            game_number,
            home_score,
            away_score
        )
