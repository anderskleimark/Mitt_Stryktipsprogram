from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from queue import Empty, Queue

from database.database import Database
from models.analysis.backtest_utils import is_cancelled, report_progress
from models.analysis_model import AnalysisModel
from models.soccer_model import SoccerModel


class BacktestParallelRunner:
    """
        Kör oberoende backtest parallellt med isolerade databasanslutningar.
    """

    def __init__(self, *, soccer_model, backtest_model_type):
        """
            Initierar parallellköraren.
        """
        self.soccer_model = soccer_model
        self.backtest_model_type = backtest_model_type

    # --------------------------------------------------
    # Körning
    # --------------------------------------------------

    def run(self, *, tasks, should_cancel=None, progress_callback=None, max_workers=None):
        """
            Kör flera backtest parallellt och returnerar resultaten i uppgiftsordning.
        """
        if not tasks:
            return []

        matches = self.soccer_model.get_matches(
            season_id=tasks[0]["season"].id)
        matches_per_run = len(matches)

        if matches_per_run <= 0:
            raise ValueError("Det finns inga matcher att backtesta.")

        results = [None] * len(tasks)
        task_progress = [0] * len(tasks)
        total_steps = matches_per_run * len(tasks)
        progress_queue = Queue()
        futures = {}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for index, task in enumerate(tasks):
                if is_cancelled(should_cancel):
                    return None

                future = executor.submit(
                    self._run_isolated,
                    should_cancel=should_cancel,
                    progress_callback=self._create_progress_reporter(
                        progress_queue, index),
                    **task
                )
                futures[future] = index

            pending = set(futures)

            while pending:
                if is_cancelled(should_cancel):
                    for future in pending:
                        future.cancel()

                    return None

                self._process_progress(
                    progress_queue,
                    task_progress,
                    matches_per_run,
                    total_steps,
                    progress_callback
                )

                done, pending = wait(pending, timeout=0.1,
                                     return_when=FIRST_COMPLETED)

                for future in done:
                    index = futures[future]
                    result = future.result()

                    if result is None:
                        for pending_future in pending:
                            pending_future.cancel()

                        return None

                    results[index] = result
                    task_progress[index] = matches_per_run
                    report_progress(progress_callback, sum(
                        task_progress), total_steps)

            self._process_progress(
                progress_queue,
                task_progress,
                matches_per_run,
                total_steps,
                progress_callback
            )

        return None if is_cancelled(should_cancel) else results

    def _run_isolated(
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
        home_advantage_mode=None,
        should_cancel=None,
        progress_callback=None,
        return_predictions=False
    ):
        """
            Kör ett backtest med egen databasanslutning och egna modeller.
        """
        if is_cancelled(should_cancel):
            return None

        database = Database(initialize=False)

        try:
            soccer_model = SoccerModel(database)
            analysis_model = AnalysisModel(database, soccer_model)
            backtest_model = self.backtest_model_type(
                soccer_model=soccer_model,
                analysis_model=analysis_model
            )

            return backtest_model.run(
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
                progress_callback=progress_callback,
                return_predictions=return_predictions
            )
        finally:
            database.close()

    # --------------------------------------------------
    # Progress
    # --------------------------------------------------

    @staticmethod
    def _create_progress_reporter(progress_queue, task_index):
        """
            Skapar en progress-callback för en executor-uppgift.
        """
        def report_task_progress(completed, _total):
            progress_queue.put((task_index, completed))

        return report_task_progress

    @staticmethod
    def _process_progress(
        progress_queue,
        task_progress,
        matches_per_run,
        total_steps,
        progress_callback
    ):
        """
            Hämtar progress från executor-trådarna och rapporterar total progress.
        """
        progress_changed = False

        while True:
            try:
                task_index, completed = progress_queue.get_nowait()
            except Empty:
                break

            completed = min(max(completed, 0), matches_per_run)

            if completed > task_progress[task_index]:
                task_progress[task_index] = completed
                progress_changed = True

        if progress_changed:
            report_progress(progress_callback, sum(task_progress), total_steps)
