from PySide6.QtWidgets import (
    QFileDialog,
    QInputDialog,
    QMessageBox
)

from models.importers.match_csv_importer import (
    MatchCsvImporter
)
from mvc import Controller


class MatchImportController(Controller):
    """
        Hanterar import av matcher från CSV-filer.
    """

    def __init__(
        self,
        *,
        view,
        competition_model
    ):
        super().__init__(view)

        self.view = view
        self.competition_model = competition_model

    def import_csv(self):
        """
            Låter användaren välja CSV-fil och
            vilken tävling matcherna tillhör.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self.view,
            "Importera matcher från CSV",
            "",
            "CSV-filer (*.csv);;Alla filer (*)"
        )

        if not file_path:
            return

        competition = (
            self._select_competition()
        )

        if competition is None:
            return

        self._import_file(
            file_path,
            competition
        )

    def _select_competition(self):
        """
            Låter användaren välja vilken tävling
            CSV-filen tillhör.
        """
        competitions = (
            self.competition_model.get_all()
        )

        if not competitions:
            QMessageBox.warning(
                self.view,
                "Importera matcher",
                "Det finns inga tävlingar registrerade."
            )

            return None

        competitions = sorted(
            competitions,
            key=lambda competition: (
                competition.country.country_name,
                competition.competition_name
            )
        )

        labels = [
            (
                f"{competition.country.country_name} - "
                f"{competition.competition_name}"
            )
            for competition in competitions
        ]

        label, accepted = QInputDialog.getItem(
            self.view,
            "Välj tävling",
            "Tävling:",
            labels,
            0,
            False
        )

        if not accepted:
            return None

        index = labels.index(
            label
        )

        return competitions[index]

    def _import_file(
        self,
        file_path,
        competition
    ):
        """
            Importerar matcher och odds från
            den valda CSV-filen.
        """
        importer = MatchCsvImporter(
            database=self.view.database,
            competition_id=competition.id
        )

        try:
            result = importer.import_file(
                file_path
            )

        except (
            OSError,
            UnicodeError,
            ValueError
        ) as exc:
            QMessageBox.critical(
                self.view,
                "Importen misslyckades",
                str(exc)
            )

            return

        self._show_result(
            result
        )

    def _show_result(
        self,
        result
    ):
        """
            Visar resultatet av importen.
        """
        QMessageBox.information(
            self.view,
            "Importen är klar",
            (
                "Importen är klar.\n\n"
                f"Rader i CSV-filen: {result.row_count}\n"
                f"Nya matcher: {result.imported_matches}\n"
                f"Uppdaterade matcher: {result.updated_matches}\n"
                f"Odds importerade: {result.imported_odds}\n"
                f"Överhoppade rader: {result.skipped_rows}"
            )
        )