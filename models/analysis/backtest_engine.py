import math

from models.domains import BacktestResult


class BacktestEngine:
    """
        Beräknar kvalitetsmått för historiska matchprognoser.
    """

    MIN_PROBABILITY = 1e-15

    def evaluate(
        self,
        predictions
    ):
        """
            Utvärderar en samling historiska
            matchprognoser.
        """
        if not predictions:
            raise ValueError(
                "Det finns inga prognoser att utvärdera."
            )

        brier_score = self._calculate_brier_score(
            predictions
        )

        log_loss = self._calculate_log_loss(
            predictions
        )

        accuracy = self._calculate_accuracy(
            predictions
        )

        return BacktestResult(
            predictions=predictions,
            matches_tested=len(predictions),
            brier_score=brier_score,
            log_loss=log_loss,
            accuracy=accuracy
        )

    def _calculate_brier_score(
        self,
        predictions
    ):
        """
            Beräknar Brier score för
            1X2-prognoser.
        """
        total_score = 0.0

        for prediction in predictions:
            actual_1 = (
                1.0
                if prediction.actual_result == "1"
                else 0.0
            )

            actual_x = (
                1.0
                if prediction.actual_result == "X"
                else 0.0
            )

            actual_2 = (
                1.0
                if prediction.actual_result == "2"
                else 0.0
            )

            score = (
                (prediction.probability_1 - actual_1) ** 2
                + (prediction.probability_x - actual_x) ** 2
                + (prediction.probability_2 - actual_2) ** 2
            )

            total_score += score

        return total_score / len(predictions)

    def _calculate_log_loss(
        self,
        predictions
    ):
        """
            Beräknar genomsnittlig log loss.
        """
        total_loss = 0.0

        for prediction in predictions:
            if prediction.actual_result == "1":
                probability = prediction.probability_1

            elif prediction.actual_result == "X":
                probability = prediction.probability_x

            else:
                probability = prediction.probability_2

            probability = max(
                probability,
                self.MIN_PROBABILITY
            )

            total_loss -= math.log(probability)

        return total_loss / len(predictions)

    def _calculate_accuracy(
        self,
        predictions
    ):
        """
            Beräknar andelen matcher där det mest
            sannolika tecknet blev rätt.
        """
        correct = 0

        for prediction in predictions:
            probabilities = {
                "1": prediction.probability_1,
                "X": prediction.probability_x,
                "2": prediction.probability_2
            }

            predicted_result = max(
                probabilities,
                key=probabilities.get
            )

            if predicted_result == prediction.actual_result:
                correct += 1

        return correct / len(predictions)
