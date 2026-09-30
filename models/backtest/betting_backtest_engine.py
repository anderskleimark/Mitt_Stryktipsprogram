from dataclasses import dataclass


@dataclass
class BettingBacktestResult:
    minimum_ev: float
    stake: float
    selection: str | None
    bets: int
    wins: int
    losses: int
    turnover: float
    return_amount: float
    profit: float
    roi: float
    hit_rate: float
    average_odds: float
    average_probability: float
    average_expected_value: float


class BettingBacktestEngine:
    DEFAULT_STAKE = 100.0
    EV_THRESHOLDS = (0.0, 0.025, 0.05, 0.075, 0.10, 0.15, 0.20)

    def evaluate(self, predictions, *, minimum_ev,
                 stake=DEFAULT_STAKE, selection=None):
        bets = [
            p for p in predictions
            if p.expected_value >= minimum_ev
            and (selection is None or p.selection == selection)
        ]
        n = len(bets)
        if not n:
            return BettingBacktestResult(
                minimum_ev, stake, selection, 0, 0, 0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            )

        wins = sum(p.won for p in bets)
        turnover = n * stake
        returned = sum(stake * p.odds for p in bets if p.won)
        profit = returned - turnover

        return BettingBacktestResult(
            minimum_ev=minimum_ev,
            stake=stake,
            selection=selection,
            bets=n,
            wins=wins,
            losses=n - wins,
            turnover=turnover,
            return_amount=returned,
            profit=profit,
            roi=profit / turnover,
            hit_rate=wins / n,
            average_odds=sum(p.odds for p in bets) / n,
            average_probability=sum(p.probability for p in bets) / n,
            average_expected_value=sum(p.expected_value for p in bets) / n
        )

    def evaluate_all(self, predictions, *, stake=DEFAULT_STAKE,
                     selection=None):
        return [
            self.evaluate(
                predictions,
                minimum_ev=t,
                stake=stake,
                selection=selection
            )
            for t in self.EV_THRESHOLDS
        ]

    def evaluate_by_selection(self, predictions, *, stake=DEFAULT_STAKE):
        return {
            s: self.evaluate_all(predictions, stake=stake, selection=s)
            for s in ("1", "X", "2")
        }
