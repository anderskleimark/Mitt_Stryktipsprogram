from dataclasses import dataclass

from models.backtest.betting_backtest_engine import BettingBacktestEngine


@dataclass
class BettingPrediction:
    """Ett möjligt historiskt 1X2-spel."""
    match_id: int
    match_date: object
    home_team: object
    away_team: object
    selection: str
    probability: float
    odds: float
    expected_value: float
    actual_result: str

    @property
    def won(self):
        return self.selection == self.actual_result


class BettingBacktest:
    """Skapar historiska spelprognoser med produktionsmodellen."""

    IGNORED_ANALYSIS_ERRORS = {
        "Hemmalaget saknas i Dixon-Coles-modellen.",
        "Bortalaget saknas i Dixon-Coles-modellen.",
        "Det finns inga färdigspelade matcher för Dixon-Coles-modellen.",
        "För få lag för Dixon-Coles-modellen.",
        "Referenstävlingen saknas i modellens matcher."
    }

    def __init__(self, *, soccer_model, analysis_model, match_odds_repository):
        self.soccer_model = soccer_model
        self.analysis_model = analysis_model
        self.match_odds_repository = match_odds_repository
        self.engine = BettingBacktestEngine()

    def run(self, *, season, odds_type="average_closing"):
        """Skapar historiska spelprognoser utan EV-filtrering."""
        matches = self.soccer_model.get_matches(season_id=season.id)
        predictions = []

        for match in matches:
            if (
                match.match_date is None
                or match.home_score is None
                or match.away_score is None
            ):
                continue

            match_odds = self.match_odds_repository.get_by_match_id(match.id)
            if match_odds is None:
                continue

            odds = self._get_odds(match_odds, odds_type)
            if odds is None:
                continue

            try:
                analysis = self.analysis_model.analyze_match(
                    season=match.season,
                    home_team=match.home_team,
                    away_team=match.away_team,
                    reference_date=match.match_date
                )
            except ValueError as error:
                if str(error) not in self.IGNORED_ANALYSIS_ERRORS:
                    raise
                continue

            result = analysis.odds_analysis.match_result
            probabilities = {
                "1": result["1"].probability,
                "X": result["X"].probability,
                "2": result["2"].probability
            }

            for selection in ("1", "X", "2"):
                probability = probabilities[selection]
                selection_odds = odds[selection]

                if (
                    probability is None
                    or selection_odds is None
                    or selection_odds <= 1.0
                ):
                    continue

                predictions.append(
                    BettingPrediction(
                        match_id=match.id,
                        match_date=match.match_date,
                        home_team=match.home_team,
                        away_team=match.away_team,
                        selection=selection,
                        probability=probability,
                        odds=selection_odds,
                        expected_value=probability * selection_odds - 1.0,
                        actual_result=match.result_1x2
                    )
                )

        return predictions

    def run_and_evaluate(
        self,
        *,
        season,
        odds_type="average_closing",
        stake=100.0
    ):
        """Skapar prognoser och utvärderar samtliga EV-gränser."""
        predictions = self.run(season=season, odds_type=odds_type)
        results = self.engine.evaluate_all(predictions, stake=stake)
        return predictions, results

    @staticmethod
    def _get_odds(match_odds, odds_type):
        odds_attributes = {
            "bet365": ("bet365_home", "bet365_draw", "bet365_away"),
            "max": ("max_home", "max_draw", "max_away"),
            "average": ("average_home", "average_draw", "average_away"),
            "bet365_closing": (
                "bet365_closing_home",
                "bet365_closing_draw",
                "bet365_closing_away"
            ),
            "max_closing": (
                "max_closing_home",
                "max_closing_draw",
                "max_closing_away"
            ),
            "average_closing": (
                "average_closing_home",
                "average_closing_draw",
                "average_closing_away"
            )
        }

        attributes = odds_attributes.get(odds_type)
        if attributes is None:
            raise ValueError(f"Okänd oddstyp: {odds_type}")

        home_odds = getattr(match_odds, attributes[0])
        draw_odds = getattr(match_odds, attributes[1])
        away_odds = getattr(match_odds, attributes[2])

        if home_odds is None and draw_odds is None and away_odds is None:
            return None

        return {"1": home_odds, "X": draw_odds, "2": away_odds}
