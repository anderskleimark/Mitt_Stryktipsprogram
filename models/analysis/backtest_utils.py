"""
    Gemensamma hjälpfunktioner för backtesting.
"""


def is_cancelled(should_cancel):
    """
        Returnerar True om pågående körning har avbrutits.
    """
    return should_cancel is not None and should_cancel()


def is_completed_match(match):
    """
        Returnerar True om matchen är färdigspelad och har matchdatum.
    """
    return (
        match.home_score is not None
        and match.away_score is not None
        and match.match_date is not None
    )


def get_result_metrics(result):
    """
        Returnerar gemensamma utvärderingsmått för ett backtestresultat.
    """
    return {
        "matches_tested": result.matches_tested,
        "brier_score": result.brier_score,
        "log_loss": result.log_loss,
        "accuracy": result.accuracy,
        "uniform_brier_score": result.uniform_brier_score,
        "uniform_log_loss": result.uniform_log_loss,
        "historical_brier_score": result.historical_brier_score,
        "historical_log_loss": result.historical_log_loss,
        "calibration_bins": result.calibration_bins
    }


def report_progress(progress_callback, completed, total):
    """
        Rapporterar progress om en callback har angetts.
    """
    if progress_callback is not None:
        progress_callback(completed, total)


def prediction_key(prediction):
    """
        Skapar en unik nyckel för en historisk prognos.
    """
    return prediction.match_date, prediction.home_team.id, prediction.away_team.id


def get_common_prediction_keys(prediction_sets):
    """
        Hämtar de matcher som finns i samtliga prognosuppsättningar.
    """
    if not prediction_sets:
        return set()

    key_sets = [
        {prediction_key(prediction) for prediction in predictions}
        for predictions in prediction_sets
    ]

    return set.intersection(*key_sets)


def filter_predictions(predictions, common_keys):
    """
        Filtrerar prognoser till matcher som finns i samtliga jämförelser.
    """
    return [
        prediction
        for prediction in predictions
        if prediction_key(prediction) in common_keys
    ]


def evaluate_common_predictions(engine, prediction_sets, error_message=None):
    """
        Utvärderar endast prognoser som finns i samtliga prognosuppsättningar.
    """
    common_keys = get_common_prediction_keys(prediction_sets)

    if not common_keys:
        raise ValueError(
            error_message or "Det finns inga gemensamma prognoser att utvärdera.")

    return [
        engine.evaluate(filter_predictions(predictions, common_keys))
        for predictions in prediction_sets
    ]
