from dataclasses import dataclass
from mvc import Model

# Klass för att hantera ett vad.


@dataclass
class Bet:
    id: int
    coupon_id: int
    system_id: int
    date: str
    correct_count: int | None = None
    prize: int | None = None

# Klass för att hantera detaljer om ett vad.


@dataclass
class BetDetails:
    bet_id: int
    match_number: int
    frame_value: str
    key_value: str | None = None
    mathematical: bool = False

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
                    key_value=row[3],
                    mathematical=row[4]
                )
            )

        return details

    # Funktion som sparar ett vad med hjälp av databasklassen.
    def update_bet_result(self, bet_id, correct, prize):
        self.database.update_bet_result(bet_id, correct, prize)

    # Funktion som sparar ett U-tecken för ett visst vad och en viss match på tipskupongen.
    def save_key(self, bet_id, match_number, key):
        self.database.save_key(
            bet_id,
            match_number,
            key
        )

    # Funktion som sparar detaljer om ett vad.
    def save_detail(self, bet_id, match_number, frame=None, key=None):
        self.database.save_detail(
            bet_id,
            match_number,
            frame,
            key
        )

    def save_mathematical(self, bet_id, match_number, checked):
        self.database.save_mathematical(bet_id, match_number, checked)

    # Funktion som raderar ett visst vad.
    def delete(self, bet_id):
        self.database.delete_bet(bet_id)
