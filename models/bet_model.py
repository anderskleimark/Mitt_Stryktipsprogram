from mvc import Model

# Klass för att hantera ett vad.


class Bet:
    def __init__(self, id, coupon_id, system_id, date, correct=None, prize=None):
        self.id = id
        self.coupon_id = coupon_id
        self.system_id = system_id
        self.date = date
        self.correct = correct
        self.prize = prize

# Klass för att hantera detaljer om ett vad.


class BetDetails:

    def __init__(
        self,
        bet_id,
        system_frame,
        key_row=None
    ):
        self.bet_id = bet_id
        self.system_frame = system_frame
        self.key_row = key_row

# Modellklass för vad.


class BetModel(Model):
    def __init__(self, database):
        super().__init__()
        self.database = database

    # Funktion för att skapa ett vad och lägga in det i databasen.
    def create_bet(
        self,
        coupon_id,
        system_id,
        date
    ):
        return self.database.create_bet(
            coupon_id,
            system_id,
            date
        )

    # Funktion som returnerar alla vad, som finns i databasen.
    def get_all(self):

        rows = self.database.get_all_bets()
        bets = []

        for row in rows:

            bets.append(
                Bet(*row)
            )

        return bets

    # Funktion som returnerar detaljer om ett angivet vad.
    def get_bet_details(self, bet_id):

        row = self.database.get_bet_details(bet_id)

        if row is None:
            return None

        return BetDetails(
            bet_id=row[0],
            system_frame=row[1],
            key_row=row[2]
        )

    # Funktion som sparar ett vad med hjälp av databasklassen.
    def update_bet_result(self, bet_id, correct, prize):
        self.database.update_bet_result(bet_id, correct, prize)
