import math

from models.domains import BacktestResult, CalibrationBin, CalibrationResult


class BacktestEngine:
    """
        Beräknar kvalitetsmått för historiska matchprognoser.
    """

    MIN_PROBABILITY = 1e-15
    CALIBRATION_BIN_COUNT = 10

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

        (
            uniform_brier_score,
            uniform_log_loss
        ) = self._calculate_uniform_scores(
            predictions
        )

        (
            historical_brier_score,
            historical_log_loss
        ) = self._calculate_historical_scores(
            predictions
        )

        calibration = self._create_calibration_result(predictions)
        calibration_1 = self._create_calibration_result(predictions, "1")
        calibration_x = self._create_calibration_result(predictions, "X")
        calibration_2 = self._create_calibration_result(predictions, "2")

        return BacktestResult(
            predictions=predictions,
            matches_tested=len(predictions),

            brier_score=brier_score,
            log_loss=log_loss,
            accuracy=accuracy,

            uniform_brier_score=uniform_brier_score,
            uniform_log_loss=uniform_log_loss,

            historical_brier_score=historical_brier_score,
            historical_log_loss=historical_log_loss,

            calibration=calibration,
            calibration_1=calibration_1,
            calibration_x=calibration_x,
            calibration_2=calibration_2

        )

    def _create_calibration_result(self, predictions, result_filter=None):
        bins = self._calculate_calibration(
            predictions,
            result_filter=result_filter
        )

        return CalibrationResult(
            bins=bins,
            ece=self._calculate_ece(bins)
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

    def _calculate_uniform_scores(
        self,
        predictions
    ):
        """
            Beräknar Brier score och log loss
            för en modell med 1/3 sannolikhet
            för 1, X och 2.
        """
        probability = 1.0 / 3.0

        total_brier = 0.0
        total_log_loss = 0.0

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

            total_brier += (
                (probability - actual_1) ** 2
                + (probability - actual_x) ** 2
                + (probability - actual_2) ** 2
            )

            total_log_loss -= math.log(
                probability
            )

        count = len(predictions)

        return (
            total_brier / count,
            total_log_loss / count
        )

    def _calculate_historical_scores(
        self,
        predictions
    ):
        """
            Beräknar Brier score och log loss
            för en historisk 1X2-baslinje.

            Endast tidigare resultat används.
            Laplace smoothing används för att
            undvika extrema startsannolikheter.
        """
        result_counts = {
            "1": 1,
            "X": 1,
            "2": 1
        }

        previous_matches = 3

        total_brier = 0.0
        total_log_loss = 0.0

        for prediction in predictions:
            probability_1 = (
                result_counts["1"]
                / previous_matches
            )

            probability_x = (
                result_counts["X"]
                / previous_matches
            )

            probability_2 = (
                result_counts["2"]
                / previous_matches
            )

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

            total_brier += (
                (probability_1 - actual_1) ** 2
                + (probability_x - actual_x) ** 2
                + (probability_2 - actual_2) ** 2
            )

            if prediction.actual_result == "1":
                probability = probability_1

            elif prediction.actual_result == "X":
                probability = probability_x

            else:
                probability = probability_2

            total_log_loss -= math.log(
                max(
                    probability,
                    self.MIN_PROBABILITY
                )
            )

            result_counts[
                prediction.actual_result
            ] += 1

            previous_matches += 1

        count = len(predictions)

        return (
            total_brier / count,
            total_log_loss / count
        )

    def _calculate_calibration(self, predictions, result_filter=None):
        """
            Beräknar kalibreringen för modellens
            1X2-sannolikheter.

            Om result_filter anges beräknas
            kalibreringen endast för det tecknet.
        """
        bins = [
            {
                "probability_sum": 0.0,
                "actual_sum": 0,
                "observations": 0
            }
            for _ in range(self.CALIBRATION_BIN_COUNT)
        ]

        for prediction in predictions:
            probabilities = {
                "1": prediction.probability_1,
                "X": prediction.probability_x,
                "2": prediction.probability_2
            }

            if result_filter is not None:
                if result_filter not in probabilities:
                    raise ValueError(
                        f"Ogiltigt kalibreringstecken: {result_filter}"
                    )

                probabilities = {
                    result_filter: probabilities[result_filter]
                }

            for result, probability in probabilities.items():
                bin_index = min(
                    int(probability * self.CALIBRATION_BIN_COUNT),
                    self.CALIBRATION_BIN_COUNT - 1
                )

                actual = 1 if prediction.actual_result == result else 0

                bins[bin_index]["probability_sum"] += probability
                bins[bin_index]["actual_sum"] += actual
                bins[bin_index]["observations"] += 1

        calibration_bins = []
        bin_width = 1.0 / self.CALIBRATION_BIN_COUNT

        for index, values in enumerate(bins):
            observations = values["observations"]

            if observations == 0:
                continue

            lower_bound = index * bin_width
            upper_bound = (index + 1) * bin_width
            average_probability = values["probability_sum"] / observations
            actual_frequency = values["actual_sum"] / observations

            calibration_bins.append(
                CalibrationBin(
                    lower_bound=lower_bound,
                    upper_bound=upper_bound,
                    average_probability=average_probability,
                    actual_frequency=actual_frequency,
                    observations=observations
                )
            )

        return calibration_bins

    def _calculate_ece(self, calibration_bins):
        """
            Beräknar Expected Calibration Error.

            Varje intervalls absoluta kalibreringsfel
            viktas med antalet observationer.
        """
        total_observations = sum(
            calibration_bin.observations
            for calibration_bin in calibration_bins
        )

        if total_observations == 0:
            return 0.0

        weighted_error = sum(
            calibration_bin.observations
            * abs(
                calibration_bin.actual_frequency
                - calibration_bin.average_probability
            )
            for calibration_bin in calibration_bins
        )

        return weighted_error / total_observations
