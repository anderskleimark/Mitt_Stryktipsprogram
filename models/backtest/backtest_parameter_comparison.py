import math
import statistics
from types import SimpleNamespace

from models.analysis.dixon_coles_model import DixonColesModel
from models.backtest.backtest_utils import (
    evaluate_common_predictions,
    filter_predictions,
    get_common_prediction_keys,
    get_result_metrics,
    is_cancelled,
    is_completed_match
)
from models.domains import (
    FormBacktestResult,
    HistoryYearsBacktestResult,
    TimeDecayBacktestResult,
    TrainingScopeBacktestResult
)


class BacktestParameterComparison:
    """
        Hanterar jämförelser mellan olika
        backtestparametrar.
    """

    def __init__(self, backtest_model):
        self.backtest_model = backtest_model

    def run_rho_comparison(
        self,
        *,
        season,
        time_decay=None,
        history_years=None,
        training_scope=None,
        should_cancel=None,
        progress_callback=None
    ):
        """
            Jämför fritt skattad rho med rho låst till 0.0
            på samma matcher.
        """
        matches = self.backtest_model.soccer_model.get_matches(
            season_id=season.id
        )

        total_steps = len(matches) * 2

        estimated_predictions = self._run_rho_variant(
            season=season,
            matches=matches,
            time_decay=time_decay,
            history_years=history_years,
            training_scope=training_scope,
            rho_mode=DixonColesModel.RHO_MODE_ESTIMATED,
            progress_offset=0,
            progress_total=total_steps,
            should_cancel=should_cancel,
            progress_callback=progress_callback
        )

        if estimated_predictions is None:
            return None

        zero_predictions = self._run_rho_variant(
            season=season,
            matches=matches,
            time_decay=time_decay,
            history_years=history_years,
            training_scope=training_scope,
            rho_mode=DixonColesModel.RHO_MODE_FIXED,
            progress_offset=len(matches),
            progress_total=total_steps,
            should_cancel=should_cancel,
            progress_callback=progress_callback
        )

        if zero_predictions is None:
            return None

        results = evaluate_common_predictions(
            self.backtest_model.engine,
            [estimated_predictions, zero_predictions],
            "Det finns inga gemensamma prognoser för rho-jämförelsen."
        )

        return [
            self._create_rho_comparison_result(
                "Skattad",
                results[0]
            ),
            self._create_rho_comparison_result(
                "0.0",
                results[1]
            )
        ]

    def _run_rho_variant(
        self,
        *,
        season,
        matches,
        time_decay,
        history_years,
        training_scope,
        rho_mode,
        progress_offset,
        progress_total,
        should_cancel,
        progress_callback
    ):
        """
            Kör en av rho-varianterna med rensad analyscache.
        """
        self.backtest_model.analysis_model.clear_analysis_caches()

        return self.backtest_model.run(
            season=season,
            time_decay=time_decay,
            history_years=history_years,
            training_scope=training_scope,
            form_weight=0.0,
            rho_mode=rho_mode,
            should_cancel=should_cancel,
            matches=matches,
            progress_callback=progress_callback,
            progress_offset=progress_offset,
            progress_total=progress_total,
            return_predictions=True
        )

    @staticmethod
    def _create_rho_comparison_result(label, result):
        """
            Skapar ett tabellkompatibelt resultat för rho-jämförelsen.
        """
        return SimpleNamespace(
            rho_label=label,
            **get_result_metrics(result)
        )

    def run_home_advantage_comparison(
        self,
        *,
        season,
        time_decay=None,
        history_years=None,
        training_scope=None,
        form_match_count=None,
        form_weight=None,
        h2h_match_count=None,
        h2h_weight=None,
        rho_mode=None,
        should_cancel=None,
        progress_callback=None
    ):
        """
            Jämför skattad hemmafördel med hemmafördel låst
            till 0.0 på exakt samma matcher.
        """
        matches = self.backtest_model.soccer_model.get_matches(
            season_id=season.id
        )

        total_steps = len(matches) * 2

        estimated_predictions = self._run_home_advantage_variant(
            season=season,
            matches=matches,
            time_decay=time_decay,
            history_years=history_years,
            training_scope=training_scope,
            form_match_count=form_match_count,
            form_weight=form_weight,
            h2h_match_count=h2h_match_count,
            h2h_weight=h2h_weight,
            rho_mode=rho_mode,
            home_advantage_mode=(
                DixonColesModel.HOME_ADVANTAGE_MODE_ESTIMATED
            ),
            progress_offset=0,
            progress_total=total_steps,
            should_cancel=should_cancel,
            progress_callback=progress_callback
        )

        if estimated_predictions is None:
            return None

        zero_predictions = self._run_home_advantage_variant(
            season=season,
            matches=matches,
            time_decay=time_decay,
            history_years=history_years,
            training_scope=training_scope,
            form_match_count=form_match_count,
            form_weight=form_weight,
            h2h_match_count=h2h_match_count,
            h2h_weight=h2h_weight,
            rho_mode=rho_mode,
            home_advantage_mode=(
                DixonColesModel.HOME_ADVANTAGE_MODE_FIXED
            ),
            progress_offset=len(matches),
            progress_total=total_steps,
            should_cancel=should_cancel,
            progress_callback=progress_callback
        )

        if zero_predictions is None:
            return None

        results = evaluate_common_predictions(
            self.backtest_model.engine,
            [
                estimated_predictions,
                zero_predictions
            ],
            "Det finns inga gemensamma prognoser för "
            "hemmafördels-jämförelsen."
        )

        common_keys = get_common_prediction_keys(
            [
                estimated_predictions,
                zero_predictions
            ]
        )

        estimated_predictions = filter_predictions(
            estimated_predictions,
            common_keys
        )

        zero_predictions = filter_predictions(
            zero_predictions,
            common_keys
        )

        return [
            self._create_home_advantage_comparison_result(
                "Skattad",
                results[0],
                estimated_predictions
            ),
            self._create_home_advantage_comparison_result(
                "0.0",
                results[1],
                zero_predictions
            )
        ]

    def _run_home_advantage_variant(
        self,
        *,
        season,
        matches,
        time_decay,
        history_years,
        training_scope,
        form_match_count,
        form_weight,
        h2h_match_count,
        h2h_weight,
        rho_mode,
        home_advantage_mode,
        progress_offset,
        progress_total,
        should_cancel,
        progress_callback
    ):
        """
            Kör en hemmafördelsvariant med rensad analyscache.
        """
        self.backtest_model.analysis_model.clear_analysis_caches()

        return self.backtest_model.run(
            season=season,
            time_decay=time_decay,
            history_years=history_years,
            training_scope=training_scope,
            form_match_count=form_match_count,
            form_weight=form_weight,
            h2h_match_count=h2h_match_count,
            h2h_weight=h2h_weight,
            rho_mode=rho_mode,
            home_advantage_mode=home_advantage_mode,
            should_cancel=should_cancel,
            matches=matches,
            progress_callback=progress_callback,
            progress_offset=progress_offset,
            progress_total=progress_total,
            return_predictions=True
        )

    @staticmethod
    def _create_home_advantage_comparison_result(
        label,
        result,
        predictions
    ):
        """
            Skapar ett tabellkompatibelt resultat
            för hemmafördels-jämförelsen.
        """
        home_advantage_values = [
            prediction.home_advantage
            for prediction in predictions
        ]

        mean_home_advantage = statistics.mean(
            home_advantage_values
        )

        median_home_advantage = statistics.median(
            home_advantage_values
        )

        goal_multiplier = math.exp(
            mean_home_advantage
        )

        return SimpleNamespace(
            home_advantage_label=label,
            home_advantage_mean=mean_home_advantage,
            home_advantage_median=median_home_advantage,
            home_advantage_minimum=min(home_advantage_values),
            home_advantage_maximum=max(home_advantage_values),
            home_advantage_goal_multiplier=goal_multiplier,
            home_advantage_goal_percentage=(
                goal_multiplier - 1.0
            ) * 100.0,
            **get_result_metrics(result)
        )

    def _run_tasks_sequentially(
        self,
        *,
        tasks,
        should_cancel=None,
        progress_callback=None
    ):
        """
            Kör oberoende backtest sekventiellt och
            rapporterar gemensam progress för alla uppgifter.
        """
        if not tasks:
            return []

        matches = self.backtest_model.soccer_model.get_matches(
            season_id=tasks[0]["season"].id
        )

        if not matches:
            raise ValueError(
                "Det finns inga matcher att backtesta."
            )

        total_steps = len(matches) * len(tasks)
        results = []

        for task_index, task in enumerate(tasks):
            if is_cancelled(should_cancel):
                return None

            # Parallellköraren använde en separat AnalysisModel
            # för varje uppgift. Rensa därför analyscachen mellan
            # uppgifterna även vid sekventiell körning.
            self.backtest_model.analysis_model.clear_analysis_caches()

            result = self.backtest_model.run(
                **task,
                should_cancel=should_cancel,
                matches=matches,
                progress_callback=progress_callback,
                progress_offset=task_index * len(matches),
                progress_total=total_steps
            )

            if result is None:
                return None

            results.append(result)

        return results

    def _run_standard_comparison(
        self,
        *,
        season,
        values,
        parameter_names,
        common_parameters,
        result_factory,
        compare_common_predictions=False,
        should_cancel=None,
        progress_callback=None
    ):
        """
            Kör en vanlig parameterjämförelse sekventiellt.
        """
        if isinstance(parameter_names, str):
            parameter_names = (parameter_names,)

        tasks = []

        for value in values:
            parameter_values = (
                value
                if isinstance(value, tuple)
                else (value,)
            )

            task = {
                "season": season,
                **common_parameters,
                **dict(zip(parameter_names, parameter_values)),
                "return_predictions": compare_common_predictions
            }

            tasks.append(task)

        results = self._run_tasks_sequentially(
            tasks=tasks,
            should_cancel=should_cancel,
            progress_callback=progress_callback
        )

        if results is None:
            return None

        if compare_common_predictions:
            results = evaluate_common_predictions(
                self.backtest_model.engine,
                results
            )

        return [
            result_factory(value, result)
            for value, result in zip(values, results)
        ]

    def run_time_decay_comparison(
        self,
        *,
        season,
        time_decay_values,
        history_years,
        training_scope,
        form_match_count=None,
        form_weight=None,
        should_cancel=None,
        progress_callback=None
    ):
        """
            Jämför flera time-decay-värden
            med samma övriga modellparametrar.
        """
        if not time_decay_values:
            raise ValueError(
                "Inga time-decay-värden har angetts."
            )

        return self._run_standard_comparison(
            season=season,
            values=time_decay_values,
            parameter_names="time_decay",
            common_parameters={
                "history_years": history_years,
                "training_scope": training_scope,
                "form_match_count": form_match_count,
                "form_weight": form_weight
            },
            result_factory=lambda value, result: TimeDecayBacktestResult(
                time_decay=value,
                **get_result_metrics(result)
            ),
            should_cancel=should_cancel,
            progress_callback=progress_callback
        )

    def run_history_years_comparison(
        self,
        *,
        season,
        history_years_values,
        time_decay,
        training_scope,
        form_match_count=None,
        form_weight=None,
        should_cancel=None,
        progress_callback=None
    ):
        """
            Jämför flera historiklängder och
            utvärderar gemensamma prognoser.
        """
        if not history_years_values:
            raise ValueError(
                "Inga historiklängder har angetts."
            )

        return self._run_standard_comparison(
            season=season,
            values=history_years_values,
            parameter_names="history_years",
            common_parameters={
                "time_decay": time_decay,
                "training_scope": training_scope,
                "form_match_count": form_match_count,
                "form_weight": form_weight
            },
            result_factory=lambda value, result: HistoryYearsBacktestResult(
                history_years=value,
                **get_result_metrics(result)
            ),
            compare_common_predictions=True,
            should_cancel=should_cancel,
            progress_callback=progress_callback
        )

    def run_training_scope_comparison(
        self,
        *,
        season,
        training_scopes,
        time_decay,
        history_years,
        form_match_count=None,
        form_weight=None,
        should_cancel=None,
        progress_callback=None
    ):
        """
            Jämför flera omfattningar av träningsdata.
        """
        if not training_scopes:
            raise ValueError(
                "Inga träningsomfattningar har angetts."
            )

        return self._run_standard_comparison(
            season=season,
            values=training_scopes,
            parameter_names="training_scope",
            common_parameters={
                "time_decay": time_decay,
                "history_years": history_years,
                "form_match_count": form_match_count,
                "form_weight": form_weight
            },
            result_factory=lambda value, result: TrainingScopeBacktestResult(
                training_scope=value,
                **get_result_metrics(result)
            ),
            should_cancel=should_cancel,
            progress_callback=progress_callback
        )

    def run_h2h_comparison(
        self,
        *,
        season,
        h2h_match_count,
        h2h_weights,
        time_decay,
        history_years,
        training_scope,
        should_cancel=None,
        progress_callback=None
    ):
        """
            Jämför H2H-vikter och utvärderar
            endast gemensamma prognoser.
        """
        if not h2h_weights:
            raise ValueError(
                "Det finns inga H2H-vikter att jämföra."
            )

        matches = self.backtest_model.soccer_model.get_matches(
            season_id=season.id
        )

        completed_matches = [
            match
            for match in matches
            if is_completed_match(match)
        ]

        eligible_matches = [
            match
            for match in completed_matches
            if self._has_required_h2h_history(
                match,
                h2h_match_count
            )
        ]

        excluded_match_count = (
            len(completed_matches)
            - len(eligible_matches)
        )

        if not eligible_matches:
            raise ValueError(
                f"Det finns inga matcher med minst "
                f"{h2h_match_count} tidigare H2H-matcher."
            )

        tasks = [
            {
                "season": season,
                "time_decay": time_decay,
                "history_years": history_years,
                "training_scope": training_scope,
                "h2h_match_count": h2h_match_count,
                "h2h_weight": h2h_weight,
                "return_predictions": True
            }
            for h2h_weight in h2h_weights
        ]

        prediction_sets = self._run_h2h_tasks(
            tasks=tasks,
            eligible_matches=eligible_matches,
            should_cancel=should_cancel,
            progress_callback=progress_callback
        )

        if prediction_sets is None:
            return None

        evaluated = evaluate_common_predictions(
            self.backtest_model.engine,
            prediction_sets,
            "Det finns inga gemensamma prognoser "
            "för H2H-jämförelsen."
        )

        return [
            SimpleNamespace(
                h2h_weight=h2h_weight,
                h2h_eligible_matches=len(
                    eligible_matches
                ),
                h2h_excluded_matches=excluded_match_count,
                h2h_required_matches=h2h_match_count,
                **get_result_metrics(result)
            )
            for h2h_weight, result in zip(
                h2h_weights,
                evaluated
            )
        ]

    def _run_h2h_tasks(
        self,
        *,
        tasks,
        eligible_matches,
        should_cancel,
        progress_callback
    ):
        """
            Kör H2H-jämförelser sekventiellt och återanvänder
            modellparametrar och H2H-förväntningar mellan vikterna.
        """
        prediction_sets = []

        total_steps = (
            len(eligible_matches) * len(tasks)
        )

        self.backtest_model.analysis_model.clear_analysis_caches()

        for task_index, task in enumerate(tasks):
            if is_cancelled(should_cancel):
                return None

            predictions = self.backtest_model.run(
                **task,
                should_cancel=should_cancel,
                matches=eligible_matches,
                progress_callback=progress_callback,
                progress_offset=(
                    task_index * len(eligible_matches)
                ),
                progress_total=total_steps
            )

            if predictions is None:
                return None

            prediction_sets.append(predictions)

        return prediction_sets

    def _has_required_h2h_history(
        self,
        match,
        required_match_count
    ):
        """
            Kontrollerar att matchen har minst
            angivet antal tidigare H2H-matcher.
        """
        h2h_matches = (
            self.backtest_model.soccer_model.get_head_to_head_matches(
                home_team_id=match.home_team.id,
                away_team_id=match.away_team.id,
                reference_date=match.match_date
            )
        )

        completed_h2h_matches = [
            h2h_match
            for h2h_match in h2h_matches
            if (
                is_completed_match(h2h_match)
                and h2h_match.match_date < match.match_date
            )
        ]

        return (
            len(completed_h2h_matches)
            >= required_match_count
        )

    def run_form_match_count_comparison(
        self,
        *,
        season,
        form_match_counts,
        form_weight,
        time_decay,
        history_years,
        training_scope,
        should_cancel=None,
        progress_callback=None
    ):
        """
            Jämför olika antal formmatcher
            med fast formvikt.
        """
        if not form_match_counts:
            raise ValueError(
                "Det finns inga antal formmatcher att jämföra."
            )

        if form_weight is None:
            raise ValueError(
                "Formvikt måste anges."
            )

        return self.run_form_comparison(
            season=season,
            form_match_counts=form_match_counts,
            form_weights=[form_weight],
            time_decay=time_decay,
            history_years=history_years,
            training_scope=training_scope,
            should_cancel=should_cancel,
            progress_callback=progress_callback
        )

    def run_form_comparison(
        self,
        *,
        season,
        form_match_counts,
        form_weights,
        time_decay,
        history_years,
        training_scope,
        should_cancel=None,
        progress_callback=None
    ):
        """
            Jämför formvikter och utvärderar
            endast gemensamma prognoser.
        """
        if not form_match_counts:
            raise ValueError(
                "Det finns inga antal formmatcher att jämföra."
            )

        if not form_weights:
            raise ValueError(
                "Det finns inga formvikter att jämföra."
            )

        combinations = [
            (form_match_count, form_weight)
            for form_match_count in form_match_counts
            for form_weight in form_weights
        ]

        return self._run_standard_comparison(
            season=season,
            values=combinations,
            parameter_names=("form_match_count", "form_weight"),
            common_parameters={
                "time_decay": time_decay,
                "history_years": history_years,
                "training_scope": training_scope
            },
            result_factory=lambda value, result: FormBacktestResult(
                form_match_count=value[0],
                form_weight=value[1],
                **get_result_metrics(result)
            ),
            compare_common_predictions=True,
            should_cancel=should_cancel,
            progress_callback=progress_callback
        )
