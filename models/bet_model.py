from models.domains import BetDetails
from mvc import Model


class BetModel(Model):
    def __init__(self, database):
        super().__init__()
        self.database = database

    def add_bet(self, coupon_id, system_id, date):
        return self.database.add_bet(coupon_id, system_id, date)

    def get_all(self):
        return self.database.bet_repository.get_all_bets()

    def get_bet_details(self, bet_id):
        return self.database.bet_repository.get_bet_details(bet_id)

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

    def update_bet_result(self, bet_id, correct, prize):
        self.database.bet_repository.update_bet_result(bet_id, correct, prize)

    def save_key(self, bet_id, match_number, key):
        self.database.bet_repository.save_key(
            bet_id,
            match_number,
            key
        )

    def save_detail(self, bet_id, match_number, frame=None, key=None):
        self.database.bet_repository.save_detail(
            bet_id,
            match_number,
            frame,
            key
        )

    def save_mathematical_value(self, bet_id, match_number, checked):
        self.database.bet_repository.save_mathematical_value(
            bet_id, match_number, checked)

    def delete(self, bet_id):
        self.database.delete_bet(bet_id)
