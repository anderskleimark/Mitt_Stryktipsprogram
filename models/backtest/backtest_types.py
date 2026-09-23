from enum import StrEnum


from enum import StrEnum


class BacktestComparison(StrEnum):
    """
        Typer av jämförelser som kan genomföras
        i ett backtest.
    """

    TIME_DECAY = "time_decay"
    HISTORY_YEARS = "history_years"
    TRAINING_SCOPE = "training_scope"
    FORM = "form"
    FORM_MATCH_COUNT = "form_match_count"
    H2H = "h2h"
    WORKER_BENCHMARK = "worker_benchmark"
    RHO_DIAGNOSTICS = "rho_diagnostics"
    RHO_COMPARISON = "rho_comparison"
    HOME_ADVANTAGE = "home_advantage"
    CALIBRATION_MODEL = "calibration_model"


class TrainingScope(StrEnum):
    """
        Omfattning av träningsdata för analysmodellen.
    """

    COUNTRY = "country"
    COMPETITION = "competition"
