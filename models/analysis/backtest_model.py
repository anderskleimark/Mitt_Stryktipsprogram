from models.analysis.backtest_engine import BacktestEngine
from models.domains import BacktestPrediction
from mvc import Model


class BacktestModel(Model):
    """
        Genomför historiska backtester av
        matchanalysmodellen.
    """

    def __init__(
        self,
        *,
        soccer_model,
        analysis_model
    ):
        self.soccer_model = soccer_model
        self.analysis_model = analysis_model

        self.engine = BacktestEngine()

    def run(
        self,
        *,
        season,
        start_date,
        end_date
    ):
        """
            Backtestar modellen på färdigspelade
            matcher inom angivet datumintervall.
        """
        matches = (
            self.soccer_model
            .get_competition_matches_between_dates(
                season.competition.id,
                start_date,
                end_date
            )
        )

        predictions = []

        for match in matches:
            if (
                match.home_score is None
                or match.away_score is None
                or match.match_date is None
            ):
                continue

            analysis = self.analysis_model.analyze_match(
                season=match.season,
                home_team=match.home_team,
                away_team=match.away_team,
                reference_date=match.match_date
            )

            predictions.append(
                self._create_prediction(
                    match,
                    analysis
                )
            )

        return self.engine.evaluate(
            predictions
        )

    def _create_prediction(
        self,
        match,
        analysis
    ):
        """
            Skapar en historisk prognos från
            matchanalysen.
        """
        match_result = (
            analysis.odds_analysis.match_result
        )

        return BacktestPrediction(
            match_date=match.match_date,

            home_team=match.home_team,
            away_team=match.away_team,

            probability_1=(
                match_result["1"].probability
            ),

            probability_x=(
                match_result["X"].probability
            ),

            probability_2=(
                match_result["2"].probability
            ),

            actual_result=match.result_1x2
        )
