from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QTableWidgetItem, QWidget

from misc.base_table_widget import BaseTableWidget
from misc.buttons import AddButton, DeleteButton, EditButton
from widgets.base_widget import BaseWidget


class CompetitionStandingWidget(BaseWidget):

    # --------------------------------------------------
    # Signaler
    # --------------------------------------------------

    selected_team_changed = Signal()
    selected_match_changed = Signal()

    # --------------------------------------------------
    # Kolumner - serietabell
    # --------------------------------------------------

    STANDING_TEAM_COLUMN = 0
    STANDING_PLAYED_COLUMN = 1
    STANDING_WON_COLUMN = 2
    STANDING_DRAW_COLUMN = 3
    STANDING_LOST_COLUMN = 4
    STANDING_GOALS_COLUMN = 5
    STANDING_POINTS_COLUMN = 6

    # --------------------------------------------------
    # Kolumner - matcher
    # --------------------------------------------------

    MATCH_DATE_COLUMN = 0
    MATCH_HOME_COLUMN = 1
    MATCH_AWAY_COLUMN = 2
    MATCH_RESULT_COLUMN = 3

    # --------------------------------------------------
    # Tabellrubriker
    # --------------------------------------------------

    STANDING_HEADERS = [
        "Lag",
        "Sp",
        "V",
        "O",
        "F",
        "Mål",
        "Poäng"
    ]

    MATCH_HEADERS = [
        "Datum",
        "Hemmalag",
        "Bortalag",
        "Resultat"
    ]

    # --------------------------------------------------
    # Etiketter
    # --------------------------------------------------

    LABEL_STANDINGS = "Serietabell"
    LABEL_STATISTICS = "Statistik"
    LABEL_MATCHES = "Matcher"

    LABEL_PLAYED = "Matcher:"
    LABEL_GOALS = "Mål:"
    LABEL_GOAL_DIFFERENCE = "Målskillnad:"
    LABEL_POINTS = "Poäng:"

    # --------------------------------------------------
    # Paneler
    # --------------------------------------------------

    LEFT_PANEL_STRETCH_FACTOR = 2
    RIGHT_PANEL_STRETCH_FACTOR = 2

    def __init__(self):
        """
            Initierar widgeten och skapar
            dess innehåll och signalanslutningar.
        """
        super().__init__()

        # Objekt
        self.standings_table = None
        self.team_info_label = None
        self.played_label = None
        self.goals_label = None
        self.goal_difference_label = None
        self.points_label = None
        self.team_matches_table = None

        self.matches_controlpanel_widget = QWidget()

        self.add_match_button = AddButton()
        self.edit_match_button = EditButton()
        self.delete_match_button = DeleteButton()

        self._build_widget()
        self._setup_signals()

    def _build_widget(self):
        """
            Skapar sidan med serietabell,
            lagstatistik och matcher.

            Vänster sida visar serietabellen.
            Höger sida visar information om valt lag,
            statistik, lagets matcher och matchkontroller.
        """

        main_layout = self.create_horizontal_layout(
            parent=None,
            spacing=30
        )

        # --------------------------------------------------
        # Paneler
        # --------------------------------------------------

        left_widget = self.create_left_panel()
        right_widget = self.create_right_panel()

        # --------------------------------------------------
        # Tillägg till huvudlayouten
        # --------------------------------------------------
        main_layout.addWidget(
            left_widget,
            stretch=self.LEFT_PANEL_STRETCH_FACTOR
        )

        main_layout.addWidget(
            right_widget,
            stretch=self.RIGHT_PANEL_STRETCH_FACTOR
        )

        self.setLayout(main_layout)

    # --------------------------------------------------
    # Vänster panel
    # --------------------------------------------------

    def create_left_panel(self):
        """
            Här skapas och returneras widgeten, 
            som används för vänster panel.
        """
        widget = QWidget()

        layout = self.create_vertical_layout(
            parent=widget,
            spacing=None
        )

        layout.addWidget(QLabel(self.LABEL_STANDINGS))

        self.standings_table = BaseTableWidget(
            readonly=True,
            rowselection=True
        )

        self.standings_table.setColumnCount(len(self.STANDING_HEADERS))
        self.standings_table.setHorizontalHeaderLabels(self.STANDING_HEADERS)
        self.standings_table.set_wide_column(self.STANDING_TEAM_COLUMN)

        self.standings_table.set_narrow_columns(
            [
                self.STANDING_PLAYED_COLUMN,
                self.STANDING_WON_COLUMN,
                self.STANDING_DRAW_COLUMN,
                self.STANDING_LOST_COLUMN,
                self.STANDING_GOALS_COLUMN,
                self.STANDING_POINTS_COLUMN
            ]
        )

        layout.addWidget(
            self.standings_table,
            stretch=1
        )
        return widget

    # --------------------------------------------------
    # Höger panel
    # --------------------------------------------------

    def create_right_panel(self):
        """
            Här skapas och returneras widgeten, 
            som används för höger panel.
        """
        widget = QWidget()
        layout = self.create_vertical_layout(
            parent=widget,
            spacing=None
        )

        self.team_info_label = QLabel()

        layout.addWidget(self.team_info_label)
        statistics_label = QLabel(self.LABEL_STATISTICS)

        statistics_label.setStyleSheet("font-weight: bold;")

        layout.addWidget(statistics_label)

        stats_widget = QWidget()

        stats_layout = self.create_grid_layout(parent=stats_widget)

        stats_layout.addWidget(
            QLabel(self.LABEL_PLAYED),
            0,
            0
        )

        self.played_label = QLabel("-")

        stats_layout.addWidget(
            self.played_label,
            0,
            1
        )

        stats_layout.addWidget(
            QLabel(self.LABEL_GOALS),
            1,
            0
        )

        self.goals_label = QLabel("-")

        stats_layout.addWidget(
            self.goals_label,
            1,
            1
        )

        stats_layout.addWidget(
            QLabel(self.LABEL_GOAL_DIFFERENCE),
            2,
            0
        )

        self.goal_difference_label = QLabel("-")

        stats_layout.addWidget(
            self.goal_difference_label,
            2,
            1
        )

        stats_layout.addWidget(
            QLabel(self.LABEL_POINTS),
            3,
            0
        )

        self.points_label = QLabel("-")

        stats_layout.addWidget(
            self.points_label,
            3,
            1
        )

        layout.addWidget(stats_widget)
        layout.addSpacing(10)

        matches_label = QLabel(self.LABEL_MATCHES)
        matches_label.setStyleSheet("font-weight: bold;")

        layout.addWidget(matches_label)

        self.team_matches_table = BaseTableWidget(
            readonly=True,
            rowselection=True
        )

        self.team_matches_table.setColumnCount(len(self.MATCH_HEADERS))
        self.team_matches_table.setHorizontalHeaderLabels(self.MATCH_HEADERS)

        self.team_matches_table.set_narrow_columns(
            [
                self.MATCH_DATE_COLUMN,
                self.MATCH_RESULT_COLUMN
            ]
        )

        self.team_matches_table.set_wide_columns(
            [
                self.MATCH_HOME_COLUMN,
                self.MATCH_AWAY_COLUMN
            ]
        )

        layout.addWidget(
            self.team_matches_table,
            stretch=1
        )

        self.create_matches_controlpanel_widget()

        layout.addWidget(self.matches_controlpanel_widget)
        return widget

    def _setup_signals(self):
        """
            Vidarebefordrar ändringar av markering
            i serietabellen och matchtabellen.
        """
        self.standings_table.itemSelectionChanged.connect(
            self.selected_team_changed.emit)

        self.team_matches_table.itemSelectionChanged.connect(
            self.selected_match_changed.emit
        )

    # --------------------------------------------------
    # Matchkontroller
    # --------------------------------------------------

    def create_matches_controlpanel_widget(self):
        """
            Skapar kontrollpanelen för att lägga till,
            redigera och ta bort matcher.
        """
        layout = self.create_horizontal_layout(
            parent=None,
            spacing=None
        )

        layout.addWidget(self.add_match_button)
        layout.addWidget(self.edit_match_button)
        layout.addWidget(self.delete_match_button)

        layout.addStretch()
        self.matches_controlpanel_widget.setLayout(layout)

    def update_standings_table(
        self,
        standings
    ):
        """
            Uppdaterar serietabellen med
            aktuell lagstatistik.
        """
        self.standings_table.blockSignals(True)

        self.standings_table.clearContents()
        self.standings_table.setRowCount(len(standings))

        # --------------------------------------------------
        # Fyll tabellen
        # --------------------------------------------------
        for row, standing in enumerate(
            standings
        ):
            self.standings_table.setItem(
                row,
                self.STANDING_TEAM_COLUMN,
                QTableWidgetItem(standing.team.display_name)
            )

            self.standings_table.setItem(
                row,
                self.STANDING_PLAYED_COLUMN,
                QTableWidgetItem(str(standing.played))
            )

            self.standings_table.setItem(
                row,
                self.STANDING_WON_COLUMN,
                QTableWidgetItem(str(standing.wins))
            )

            self.standings_table.setItem(
                row,
                self.STANDING_DRAW_COLUMN,
                QTableWidgetItem(str(standing.draws))
            )

            self.standings_table.setItem(
                row,
                self.STANDING_LOST_COLUMN,
                QTableWidgetItem(str(standing.losses))
            )

            self.standings_table.setItem(
                row,
                self.STANDING_GOALS_COLUMN,
                QTableWidgetItem(
                    f"{standing.goals_for} – "
                    f"{standing.goals_against}"
                )
            )

            self.standings_table.setItem(
                row,
                self.STANDING_POINTS_COLUMN,
                QTableWidgetItem(str(standing.points))
            )

        # --------------------------------------------------
        # Bredd på kolumnerna
        # --------------------------------------------------

        self.standings_table.set_wide_column(self.STANDING_TEAM_COLUMN)
        self.standings_table.set_narrow_columns(
            [
                self.STANDING_PLAYED_COLUMN,
                self.STANDING_WON_COLUMN,
                self.STANDING_DRAW_COLUMN,
                self.STANDING_LOST_COLUMN,
                self.STANDING_GOALS_COLUMN,
                self.STANDING_POINTS_COLUMN
            ]
        )

        self.standings_table.blockSignals(False)

    def update_team_statistics(
        self,
        standing
    ):
        """
            Uppdaterar statistikfältet för
            det valda laget.
        """
        self.team_info_label.setText(standing.team.display_name)

        self.played_label.setText(str(standing.played))

        self.goals_label.setText(
            f"{standing.goals_for} – {standing.goals_against}")

        goal_difference = standing.goals_for - standing.goals_against

        self.goal_difference_label.setText(f"{goal_difference:+d}")
        self.points_label.setText(str(standing.points))

    def update_team_matches(
        self,
        matches
    ):
        """
            Uppdaterar matchtabellen med matcher för valt lag.
        """
        self.team_matches_table.blockSignals(True)
        self.team_matches_table.clearContents()

        self.team_matches_table.setRowCount(len(matches))

        for row, match in enumerate(
            matches
        ):
            self.team_matches_table.setItem(
                row,
                self.MATCH_DATE_COLUMN,
                QTableWidgetItem(str(match.match_date))
            )

            self.team_matches_table.setItem(
                row,
                self.MATCH_HOME_COLUMN,
                QTableWidgetItem(match.home_team.display_name)
            )

            self.team_matches_table.setItem(
                row,
                self.MATCH_AWAY_COLUMN,
                QTableWidgetItem(match.away_team.display_name)
            )

            result = ""

            if match.home_score is not None and match.away_score is not None:
                result = f"{match.home_score} – {match.away_score}"

            self.team_matches_table.setItem(
                row,
                self.MATCH_RESULT_COLUMN,
                QTableWidgetItem(result)
            )

        self.team_matches_table.set_narrow_columns(
            [
                self.MATCH_DATE_COLUMN,
                self.MATCH_RESULT_COLUMN
            ]
        )

        self.team_matches_table.set_wide_columns(
            [
                self.MATCH_HOME_COLUMN,
                self.MATCH_AWAY_COLUMN
            ]
        )
        self.team_matches_table.blockSignals(False)

    def set_add_match_button_status(
        self,
        status
    ):
        """
            Aktiverar eller inaktiverar knappen
            för att lägga till en match.
        """
        self.add_match_button.setEnabled(status)

    def set_edit_match_button_status(
        self,
        status
    ):
        """
            Aktiverar eller inaktiverar knappen
            för att redigera en match.
        """
        self.edit_match_button.setEnabled(status)

    def set_delete_match_button_status(
        self,
        status
    ):
        """
            Aktiverar eller inaktiverar knappen
            för att ta bort en match.
        """
        self.delete_match_button.setEnabled(status)

    def get_selected_team_row(self):
        """
            Returnerar vald rad i
            serietabellen.
        """
        return self.standings_table.get_selected_row()

    def get_selected_match_row(self):
        """
            Returnerar vald rad i
            matchtabellen.
        """
        return self.team_matches_table.get_selected_row()

    def select_team_row(
        self,
        row
    ):
        """
            Markerar angiven rad
            i serietabellen.
        """
        self.standings_table.selectRow(row)

    def clear_selection(self):
        """
            Rensar markeringarna i serietabellen
            och matchtabellen.
        """
        self.standings_table.clear_current_selection()
        self.team_matches_table.clear_current_selection()

    def clear_team_information(self):
        """
            Rensar informationen och matchlistan
            för det valda laget.
        """
        self.team_info_label.setText("Laginformation")

        self.played_label.setText("-")
        self.goals_label.setText("-")
        self.goal_difference_label.setText("-")
        self.points_label.setText("-")

        self.team_matches_table.blockSignals(True)

        self.team_matches_table.clear_current_selection()
        self.team_matches_table.clearContents()
        self.team_matches_table.setRowCount(0)

        self.team_matches_table.blockSignals(False)

    def get_active_selection_table(self):
        """
            Returnerar den aktiva tabellen i serietabellsvyn.
        """
        if self.standings_table.selectedItems():
            return self.standings_table

        if self.team_matches_table.selectedItems():
            return self.team_matches_table

        return None

    def is_standings_table(
        self,
        table
    ):
        """
            Returnerar True om angiven tabell är serietabellen.
        """
        return table is self.standings_table
