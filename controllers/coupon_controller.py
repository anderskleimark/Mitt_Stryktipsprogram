from PySide6.QtGui import QTextDocument
from PySide6.QtPrintSupport import QPrintDialog, QPrinter

from models.domains import Country, CouponMatch, SoccerMatch
from mvc import Controller


class CouponController(Controller):
    """
        Controller för hantering av stryktipskuponger.

        Ansvarar för att skapa, läsa, uppdatera, skriva ut
        och ta bort kuponger samt synkronisera information
        mellan modell och vy.
    """

    # Konstanter
    HOME_SCORE_COLUMN = 3
    AWAY_SCORE_COLUMN = 4
    RESULT_COLUMN = 5

    HTML_TABLE_BORDER = 1
    HTML_CELL_SPACING = 0
    HTML_CELL_PADDING = 5
    HTML_TABLE_WIDTH = "100%"

    FLAG_WIDTH = 20
    FLAG_HEIGHT = 14

    WARNING_TITLE = "Fel"
    DELETE_TITLE = "Radera kupong"
    DELETE_TEXT = "Är du säker på att du vill radera kupongen?"
    NO_HOME_TEAM_TEXT = "Hemmalag saknas i match"
    NO_AWAY_TEAM_TEXT = "Bortalag saknas i match"
    NO_LEAGUE_TEXT = "Liga saknas i match"

    def __init__(
        self,
        *,
        coupon_model,
        soccer_model,
        team_model,
        view
    ):
        """
            Initierar controllern.

            Kopplar samman modell och vy, registrerar
            signaler samt laddar aktuell kupong.
        """
        super().__init__(view)
        self.coupon_model = coupon_model
        self.soccer_model = soccer_model
        self.team_model = team_model
        self.add_connections()

        self.load_coupon()
        self.view.enter_view_mode()

    def add_connections(self):
        """
            Kopplar vyens signaler till controller-metoder.
        """
        self.view.year_week_widget.year_week_changed.connect(
            self.on_year_week_changed)
        self.view.save_button.clicked.connect(self.on_save_button_clicked)
        self.view.add_coupon_button.clicked.connect(self.on_add_coupon_clicked)
        self.view.back_button.clicked.connect(self.on_back_button_clicked)
        self.view.print_button.clicked.connect(self.on_print_clicked)
        self.view.delete_button.clicked.connect(self.on_delete_clicked)
        self.view.coupon_table.itemChanged.connect(self.on_item_changed)
        self.view.season_changed.connect(self.on_season_changed)

    def on_year_week_changed(self):
        """
            Laddar kupongen när vald år/omgång ändras.
        """
        self.load_coupon()

    def on_item_changed(self, item):
        """
            Uppdaterar resultatet för en match när användaren
            ändrar hemma- eller bortamål i tabellen.
        """
        row = item.row()
        col = item.column()

        # Endast hemmamål och bortamål
        if col not in (
            self.HOME_SCORE_COLUMN,
            self.AWAY_SCORE_COLUMN
        ):
            return

        home_item = self.view.coupon_table.item(
            row,
            self.HOME_SCORE_COLUMN
        )

        away_item = self.view.coupon_table.item(
            row,
            self.AWAY_SCORE_COLUMN
        )

        if home_item is None or away_item is None:
            return

        try:
            home_score = int(home_item.text().strip())
            away_score = int(away_item.text().strip())

        except ValueError:
            return

        coupon = self.coupon_model.current_coupon

        if coupon is None:
            return

        coupon_match = coupon.soccer_matches[row]
        match = coupon_match.soccer_match

        match.home_score = home_score
        match.away_score = away_score

        self.coupon_model.update_match_score(
            coupon.id,
            coupon_match.match_number,
            home_score,
            away_score
        )

        self.view.coupon_table.blockSignals(True)
        result_item = self.view.coupon_table.item(
            row,
            self.RESULT_COLUMN
        )

        result_item.setText(
            match.result_1x2
        )

        self.view.coupon_table.blockSignals(False)

    def on_save_button_clicked(self):
        """
            Sparar en ny kupong med tillhörande matcher.

            Validerar att samtliga matcher innehåller
            lag och liga innan kupongen skapas.
        """
        year = self.view.year_week_widget.get_year()
        week = self.view.year_week_widget.get_week()

        raw_matches = self.view.get_coupon_matches()

        coupon_matches = []
        for data in raw_matches:
            if not data["home_team_id"]:
                self.view.show_warning(
                    self.WARNING_TITLE,
                    f"{self.NO_HOME_TEAM_TEXT} {data['number']}."
                )
                return

            if not data["away_team_id"]:
                self.view.show_warning(
                    self.WARNING_TITLE,
                    f"{self.NO_AWAY_TEAM_TEXT} {data['number']}."
                )
                return

            if data["season_id"] is None:
                self.view.show_warning(
                    self.WARNING_TITLE,
                    f"{self.NO_LEAGUE_TEXT} {data['number']}."
                )
                return

            season = self.soccer_model.get_season_by_id(
                data["season_id"]
            )

            if season is None:
                self.view.show_warning(
                    self.WARNING_TITLE,
                    f"Säsong saknas i match {data['number']}."
                )
                return

            home_team = self.team_model.get_team_by_id(
                data["home_team_id"]
            )

            away_team = self.team_model.get_team_by_id(
                data["away_team_id"]
            )

            match = SoccerMatch(
                id=None,
                season=season,
                home_team=home_team,
                away_team=away_team
            )

            coupon_matches.append(
                CouponMatch(
                    data["number"],
                    match
                )
            )

        coupon_id = self.coupon_model.add_coupon_with_matches(
            year,
            week,
            coupon_matches
        )

        self.coupon_model.current_coupon = self.coupon_model.get(coupon_id)
        self.load_coupon()
        self.view.enter_view_mode()

    def on_add_coupon_clicked(self):
        """
            Växlar till läget för att skapa en ny kupong.
        """
        self.view.enter_create_mode()
        seasons = self.soccer_model.get_all_seasons()
        self.view.set_seasons(seasons)

    def on_back_button_clicked(self):
        """
            Återgår till visningsläge och laddar om
            den aktuella kupongen.
        """
        self.view.enter_view_mode()

        # Ladda om aktuell vecka/omgång så rätt läge sätts
        self.load_coupon()

    def on_print_clicked(self):
        """
            Skriver ut den aktuella kupongen.
        """
        year = self.view.year_week_widget.get_year()
        week = self.view.year_week_widget.get_week()

        coupon = self.coupon_model.get_by_year_week(year, week)

        if coupon is None:
            return

        document = QTextDocument()
        document.setHtml(
            self.create_coupon_html(coupon)
        )

        printer = QPrinter()
        dialog = QPrintDialog(printer, self.view)

        if dialog.exec():
            document.print_(printer)

    def on_delete_clicked(self):
        """
            Raderar den aktuella kupongen efter att
            användaren har bekräftat åtgärden.
        """
        confirmed = self.view.ask_confirmation(
            self.DELETE_TITLE,
            self.DELETE_TEXT
        )

        if not confirmed:
            return

        coupon = self.coupon_model.current_coupon

        if coupon is None:
            return

        self.coupon_model.delete(coupon.id)

        self.coupon_model.current_coupon = None

        self.load_coupon()

    def on_season_changed(self, row, season_id):
        """
            Uppdaterar listan med lag när en säsong
            ändras för en match.
        """
        teams = self.soccer_model.get_teams_in_season(
            season_id
        )

        self.view.set_teams(
            row,
            teams
        )

    def create_coupon_html(self, coupon):
        """
            Skapar HTML-representationen av en kupong.
            Används vid utskrift av kupongen.
        """
        html = f"""
        <h1>Stryktipskupong</h1>

        <p>
            <b>År:</b> {coupon.coupon_year}<br>
            <b>Omgång:</b> {coupon.coupon_week}
        </p>

        <table
            border="{self.HTML_TABLE_BORDER}"
            cellspacing="{self.HTML_CELL_SPACING}"
            cellpadding="{self.HTML_CELL_PADDING}"
            width="{self.HTML_TABLE_WIDTH}"
        >
            <tr>
                <th>Nr</th>
                <th>Liga</th>
                <th>Hemmalag</th>
                <th>Bortalag</th>
                <th>Resultat</th>
            </tr>
        """

        for coupon_match in coupon.soccer_matches:
            match = coupon_match.soccer_match

            flag_path = Country.get_flag_path(
                match.season.competition.country.country_name
            )

            if flag_path:
                league = (
                    f'<img src="{flag_path}" '
                    f'width="{self.FLAG_WIDTH}" height="{self.FLAG_HEIGHT}"> '
                    f'{match.season.competition.competition_name}'
                )
            else:
                league = match.season.competition.competition_name

            html += f"""
            <tr>
                <td>{coupon_match.match_number}</td>
                <td>{league}</td>
                <td>{match.home_team}</td>
                <td>{match.away_team}</td>
                <td>{match.result_1x2}</td>
            </tr>
            """

        html += "</table>"

        return html

    def load_coupon(self):
        """
            Läser in kupongen för vald årgång och omgång.

            Uppdaterar vy och modell beroende på om
            kupongen finns eller inte.
        """
        year = self.view.year_week_widget.get_year()
        week = self.view.year_week_widget.get_week()

        # Fyll tävling/liga-comboboxarna först.
        seasons = self.soccer_model.get_all_seasons()
        self.view.set_seasons(seasons)

        coupon = self.coupon_model.get_by_year_week(
            year,
            week
        )

        # Ingen kupong finns för vald vecka
        if coupon is None:
            self.coupon_model.current_coupon = None
            self.view.set_buttons_enabled(False)
            self.view.update_coupon_matches([])

            self.view.add_coupon_button.setEnabled(True)
            self.view.coupon_table.setEnabled(False)

            return

        # Kupong finns
        self.coupon_model.current_coupon = coupon

        self.view.add_coupon_button.setEnabled(False)
        self.view.coupon_table.setEnabled(True)

        # Visa ligor och resultat
        self.view.update_coupon_matches(
            coupon.soccer_matches
        )

        # Ladda lagen efter att ligan är vald.
        for row, coupon_match in enumerate(
            coupon.soccer_matches
        ):
            match = coupon_match.soccer_match

            if match.season.id is None:
                continue

            teams = self.soccer_model.get_teams_in_season(
                match.season.id
            )

            self.view.set_teams(
                row,
                teams,
                match.home_team.id,
                match.away_team.id
            )

    def clear_form(self):
        """
            Återställer formuläret i vyn.
        """
        self.view.clear_form()
