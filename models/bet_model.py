from models.domains import Bet, BetDetails, Coupon, System
from mvc import Model

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
            bet = Bet(
                id=row["id"],
                date=row["date"],
                correct_count=row["correct_count"],
                prize=row["prize"],
                system=System(
                    id=row["system_id"],
                    system_type=row["system_type"],
                    full_covers=row["full_covers"],
                    half_covers=row["half_covers"],
                    rows=row["rows"]
                ),
                coupon=Coupon(
                    id=row["coupon_id"],
                    year=row["year"],
                    week=row["week"],
                )
            )
            bets.append(bet)

        return bets

    # Funktion som returnerar detaljer om ett angivet vad.
    def get_bet_details(self, bet_id):
        rows = self.database.get_bet_details(bet_id)
        details = []

        for row in rows:
            details.append(
                BetDetails(
                    bet_id=row["bet_id"],
                    match_number=row["match_number"],
                    frame_value=row["frame_value"],
                    key_value=row["key_value"],
                    mathematical=row["mathematical"]
                )
            )

        return details

    def get_price_factor(self, bet_id):
        factor = 1

        details = self.get_bet_details(bet_id)

        for detail in details:
            if detail.mathematical:
                frame_value = detail.frame_value

                if frame_value in {"1X", "12", "X2"}:
                    factor *= 2
                elif frame_value == "1X2":
                    factor *= 3

        return factor

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
