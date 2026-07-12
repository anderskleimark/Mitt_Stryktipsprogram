from mvc import Model

# Klass för att hantera ett vad.


class Bet:
    def __init__(self, id, coupon_id, system_id, date, correct_count=None, prize=None):
        self.id = id
        self.coupon_id = coupon_id
        self.system_id = system_id
        self.date = date
        self.correct_count = correct_count
        self.prize = prize

# Klass för att hantera detaljer om ett vad.


class BetDetails:

    def __init__(
        self,
        bet_id,
        match_number,
        frame_value,
        key_value=None
    ):
        self.bet_id = bet_id
        self.match_number = match_number
        self.frame_value = frame_value
        self.key_value = key_value

# Modellklass för vad.


class BetModel(Model):
    def __init__(self, database):
        super().__init__()
        self.database = database

    # Funktion för att skapa ett vad och lägga in det i databasen.
    def create_bet(self, coupon_id, system_id, date):
        return self.database.create_bet(coupon_id, system_id, date)

    # Funktion som returnerar alla vad, som finns i databasen.
    def get_all(self):

        rows = self.database.get_all_bets()
        bets = []

        for row in rows:
            bets.append(Bet(*row))

        return bets

    # Funktion som returnerar detaljer om ett angivet vad.
    def get_bet_details(self, bet_id):

        rows = self.database.get_bet_details(bet_id)

        details = []

        for row in rows:

            details.append(
                BetDetails(
                    bet_id=row[0],
                    match_number=row[1],
                    frame_value=row[2],
                    key_value=row[3]
                )
            )

        return details

    # Funktion som sparar ett vad med hjälp av databasklassen.
    def update_bet_result(self, bet_id, correct, prize):
        self.database.update_bet_result(bet_id, correct, prize)

    # Funktion som sparar värdet på ramen för en viss match.
    def save_frame(self, bet_id, match_number, frame):

        self.database.save_frame(
            bet_id,
            match_number,
            frame
        )
