import math

from scipy.optimize import minimize_scalar

from models.domains import BacktestPrediction


class ProbabilityCalibrationModel:
    """
        Kalibrerar 1X2-sannolikheter genom att justera
        modellens sannolikhetsskärpa.

        beta = 1.0 innebär oförändrade sannolikheter.
        beta < 1.0 gör sannolikheterna mindre extrema.
        beta > 1.0 gör sannolikheterna mer extrema.
    """

    MIN_BETA = 0.25
    MAX_BETA = 2.50
    MIN_PROBABILITY = 1e-15

    def __init__(self):
        self.beta = 1.0

    def fit(self, predictions):
        """
            Skattar beta genom att minimera log loss
            på träningsprognoserna.
        """
        if not predictions:
            raise ValueError(
                "Det finns inga prognoser att kalibrera modellen med."
            )

        result = minimize_scalar(
            lambda beta: self._calculate_log_loss(predictions, beta),
            bounds=(self.MIN_BETA, self.MAX_BETA),
            method="bounded"
        )

        if not result.success:
            raise ValueError("Kalibreringsmodellen kunde inte skattas.")

        self.beta = float(result.x)
        return self.beta

    def transform(self, predictions):
        """
            Returnerar nya prognoser med kalibrerade sannolikheter.
        """
        return [
            self._transform_prediction(prediction)
            for prediction in predictions
        ]

    def _transform_prediction(self, prediction):
        probability_1, probability_x, probability_2 = (
            self._calibrate_probabilities(
                prediction.probability_1,
                prediction.probability_x,
                prediction.probability_2,
                self.beta
            )
        )

        return BacktestPrediction(
            match_date=prediction.match_date,
            home_team=prediction.home_team,
            away_team=prediction.away_team,
            probability_1=probability_1,
            probability_x=probability_x,
            probability_2=probability_2,
            actual_result=prediction.actual_result,
            home_advantage=prediction.home_advantage
        )

    def _calculate_log_loss(self, predictions, beta):
        total_loss = 0.0

        for prediction in predictions:
            probability_1, probability_x, probability_2 = (
                self._calibrate_probabilities(
                    prediction.probability_1,
                    prediction.probability_x,
                    prediction.probability_2,
                    beta
                )
            )

            probabilities = {
                "1": probability_1,
                "X": probability_x,
                "2": probability_2
            }

            probability = probabilities[prediction.actual_result]
            probability = max(probability, self.MIN_PROBABILITY)

            total_loss -= math.log(probability)

        return total_loss / len(predictions)

    @staticmethod
    def _calibrate_probabilities(
        probability_1,
        probability_x,
        probability_2,
        beta
    ):
        values = (
            probability_1 ** beta,
            probability_x ** beta,
            probability_2 ** beta
        )

        total = sum(values)

        return tuple(value / total for value in values)
