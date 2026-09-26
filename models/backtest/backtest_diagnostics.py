import math
import statistics

import numpy as np

from models.analysis.dixon_coles_model import DixonColesModel
from models.backtest.backtest_utils import is_completed_match


class BacktestDiagnostics:
    """
        Hanterar diagnostiska backtester och
        sammanställningar av diagnostiska värden.
    """

    RHO_BOUND_TOLERANCE = 0.001

    def __init__(self, backtest_model):
        self.backtest_model = backtest_model

    def run_rho_diagnostics(
        self,
        *,
        season,
        time_decay=None,
        history_years=None,
        training_scope=None,
        should_cancel=None,
        matches=None,
        progress_callback=None
    ):
        """
            Kör ett backtest och sammanställer skattade rho-värden.
        """
        self.backtest_model.analysis_model.clear_analysis_caches()
        self.backtest_model.analysis_model.clear_rho_diagnostics()

        if matches is None:
            matches = self.backtest_model.soccer_model.get_matches(
                season_id=season.id
            )

        completed_matches = [
            match
            for match in matches
            if is_completed_match(match)
        ]

        match_dates = {
            match.match_date
            for match in completed_matches
        }

        result = self.backtest_model.run(
            season=season,
            time_decay=time_decay,
            history_years=history_years,
            training_scope=training_scope,
            form_weight=0.0,
            rho_mode=DixonColesModel.RHO_MODE_ESTIMATED,
            should_cancel=should_cancel,
            matches=matches,
            progress_callback=progress_callback
        )

        if result is None:
            return None

        diagnostics = (
            self.backtest_model.analysis_model.get_rho_diagnostics()
        )

        if not diagnostics:
            raise ValueError(
                "Inga rho-värden samlades in under backtestet."
            )

        return self._create_rho_diagnostics_result(
            result,
            completed_matches,
            match_dates,
            diagnostics
        )

    def _create_rho_diagnostics_result(
        self,
        result,
        completed_matches,
        match_dates,
        diagnostics
    ):
        """
            Skapar sammanställningen för rho-diagnostiken.
        """
        rho_values = [
            item["rho"]
            for item in diagnostics
        ]

        reference_dates = [
            item["reference_date"]
            for item in diagnostics
        ]

        unique_reference_dates = set(
            reference_dates
        )

        missing_reference_dates = sorted(
            match_dates - unique_reference_dates
        )

        extra_reference_dates = sorted(
            unique_reference_dates - match_dates
        )

        model = (
            self.backtest_model.analysis_model.engine.dixon_coles_model
        )

        lower_bound = model.RHO_MIN
        upper_bound = model.RHO_MAX

        lower_bound_count = sum(
            math.isclose(
                rho,
                lower_bound,
                rel_tol=0.0,
                abs_tol=self.RHO_BOUND_TOLERANCE
            )
            for rho in rho_values
        )

        upper_bound_count = sum(
            math.isclose(
                rho,
                upper_bound,
                rel_tol=0.0,
                abs_tol=self.RHO_BOUND_TOLERANCE
            )
            for rho in rho_values
        )

        count = len(rho_values)

        return {
            "backtest_result": result,
            "match_count": len(completed_matches),
            "match_date_count": len(match_dates),
            "count": count,
            "reference_date_count": len(
                unique_reference_dates
            ),
            "duplicate_reference_date_count": (
                count - len(unique_reference_dates)
            ),
            "missing_reference_date_count": len(
                missing_reference_dates
            ),
            "extra_reference_date_count": len(
                extra_reference_dates
            ),
            "missing_reference_dates": missing_reference_dates,
            "extra_reference_dates": extra_reference_dates,
            "minimum": min(rho_values),
            "percentile_05": float(
                np.percentile(rho_values, 5)
            ),
            "mean": statistics.mean(rho_values),
            "median": statistics.median(rho_values),
            "percentile_95": float(
                np.percentile(rho_values, 95)
            ),
            "maximum": max(rho_values),
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "lower_bound_count": lower_bound_count,
            "upper_bound_count": upper_bound_count,
            "lower_bound_percentage": (
                lower_bound_count / count * 100.0
            ),
            "upper_bound_percentage": (
                upper_bound_count / count * 100.0
            ),
            "values": diagnostics
        }

