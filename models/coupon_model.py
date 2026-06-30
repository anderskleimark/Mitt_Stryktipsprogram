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
        self.current_coupon = None

    # Funktion för att lägga till en ny tipskupong i databasen.
    def create_coupon(self, year, week):
        self.database.create_coupon(year, week)

    # Funktion som returnerar en viss tipskupong och matcher med hjälp av år och månad.
    def get_coupon(self, year, week):
        data = self.database.get_coupon(year, week)

        if data is None:
            self.current_coupon = None
            return None

        coupon_id, year, week = data

        rows = self.database.get_games(coupon_id)

        games = []

        for number, home_team, away_team, home_score, away_score in rows:
            games.append(
                Game(
                    number,
                    home_team,
                    away_team,
                    home_score,
                    away_score
                )
            )

        coupon = Coupon(coupon_id, year, week, games)

        # 🔥 viktig rad
        self.current_coupon = coupon

        return coupon

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
