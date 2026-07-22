from PySide6.QtGui import QTextDocument
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtWidgets import QMessageBox

from misc.country import Country
from mvc import Controller
from models.domains import SoccerMatch, Coupon, CouponMatch

# En Controller-klass, som samarbetar med vyn som visar tillagda tipskuponger.


class CouponController(Controller):
    def __init__(self, model, view):
        super().__init__(model, view)
        self.add_connections()

        # Hämta alla säsonger en gång
        seasons = self.model.get_all_seasons()
        self.load_coupon()
        self.view.enter_view_mode()

    def add_connections(self):
        self.view.year_week_widget.year_week_changed.connect(
            self.on_year_week_changed)
        self.view.save_button.clicked.connect(self.on_save_button_clicked)
        self.view.add_coupon_button.clicked.connect(self.on_add_coupon_clicked)
        self.view.back_button.clicked.connect(self.on_back_button_clicked)
        self.view.print_button.clicked.connect(self.on_print_clicked)
        self.view.delete_button.clicked.connect(self.on_delete_clicked)
        self.view.game_table.itemChanged.connect(self.on_item_changed)
        self.view.season_changed.connect(self.on_season_changed)

    # Funktion som körs, om året eller veckan ändras.
    def on_year_week_changed(self):
        self.load_coupon()

    # Funktion som körs, om någonting ändras i tabellen.
    def on_item_changed(self, item):
        row = item.row()
        col = item.column()

        # Endast hemmamål och bortamål
        if col not in (3, 4):
            return

        home_item = self.view.game_table.item(row, 3)
        away_item = self.view.game_table.item(row, 4)

        if home_item is None or away_item is None:
            return

        try:
            home_score = int(home_item.text().strip())
            away_score = int(away_item.text().strip())

        except ValueError:
            return

        coupon = self.model.current_coupon

        if coupon is None:
            return

        coupon_match = coupon.soccer_matches[row]
        match = coupon_match.soccer_match

        match.home_score = home_score
        match.away_score = away_score

        self.model.update_match_score(
            coupon.id,
            coupon_match.number,
            home_score,
            away_score
        )

        self.view.game_table.blockSignals(True)
        result_item = self.view.game_table.item(row, 5)

        result_item.setText(
            match.result_1x2
        )

        self.view.game_table.blockSignals(False)

    # Funktion för att spara en tipskupong.
    def on_save_button_clicked(self):
        year = self.view.year_week_widget.get_year()
        week = self.view.year_week_widget.get_week()

        raw_matches = self.view.get_coupon_matches()

        coupon_matches = []
        for data in raw_matches:
            if not data["home_team"]:
                QMessageBox.warning(
                    self.view,
                    "Fel",
                    f"Hemmalag saknas i match {data['number']}."
                )
                return

            if not data["away_team"]:
                QMessageBox.warning(
                    self.view,
                    "Fel",
                    f"Bortalag saknas i match {data['number']}."
                )
                return

            if data["season_id"] is None:
                QMessageBox.warning(
                    self.view,
                    "Fel",
                    f"Liga saknas i match {data['number']}."
                )
                return

            competition = self.model.get_competition_by_season(
                data["season_id"]
            )

            match = SoccerMatch(
                id=None,
                season_id=data["season_id"],
                competition=competition,
                home_team=data["home_team"],
                away_team=data["away_team"]
            )

            coupon_matches.append(
                CouponMatch(
                    data["number"],
                    match
                )
            )

        coupon_id = self.model.create_coupon_with_matches(
            year,
            week,
            coupon_matches
        )

        self.model.current_coupon = self.model.get(coupon_id)
        self.load_coupon()
        self.view.enter_view_mode()

    # Funktion för att visa formuläret för att lägga till en tipskupong.
    def on_add_coupon_clicked(self):
        self.view.enter_create_mode()
        seasons = self.model.get_all_seasons()
        self.view.set_seasons(seasons)

    # Funktion för att komma till "visaläget".
    def on_back_button_clicked(self):
        self.view.enter_view_mode()

        # Ladda om aktuell vecka/omgång så rätt läge sätts
        self.load_coupon()

    # Funktion som hanterar händelser, om använder trycker på "Skriv ut".
    def on_print_clicked(self):
        year = self.view.year_week_widget.get_year()
        week = self.view.year_week_widget.get_week()

        coupon = self.model.get_by_year_week(year, week)

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

    # Funktion för interaktion, om användaren trycker på "radera".
    def on_delete_clicked(self):
        message = QMessageBox(self.view)
        message.setIcon(QMessageBox.Icon.Warning)
        message.setWindowTitle("Radera kupong")
        message.setText("Är du säker på att du vill radera kupongen?")
        message.setInformativeText("Denna åtgärd kan inte ångras.")
        message.setStandardButtons(
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
        )
        message.setDefaultButton(QMessageBox.StandardButton.Cancel)

        reply = message.exec()
        if reply == QMessageBox.StandardButton.Ok:
            print("OK")
        else:
            print("Avbryt")

    # Funktion som triggas, när användaren ändrar säsong.
    def on_season_changed(self, row, season_id):
        teams = self.model.get_teams(season_id)

        self.view.set_teams(
            row,
            teams
        )

    # Funktion som har hand om skapandet av den html som behövs vid utskrift av kuponger.
    def create_coupon_html(self, coupon):
        html = f"""
        <h1>Stryktipskupong</h1>

        <p>
            <b>År:</b> {coupon.year}<br>
            <b>Omgång:</b> {coupon.week}
        </p>

        <table border="1" cellspacing="0" cellpadding="5" width="100%">

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
                match.competition.country
            )

            if flag_path:
                league = (
                    f'<img src="{flag_path}" '
                    f'width="20" height="14"> '
                    f'{match.competition.name}'
                )
            else:
                league = match.competition.name

            html += f"""
            <tr>
                <td>{coupon_match.number}</td>
                <td>{league}</td>
                <td>{match.home_team}</td>
                <td>{match.away_team}</td>
                <td>{match.result_1x2}</td>
            </tr>
            """

        html += "</table>"

        return html

    # Funktion för att ladda en tipskupong utifrån vad som har valts i vyn.
    def load_coupon(self):
        year = self.view.year_week_widget.get_year()
        week = self.view.year_week_widget.get_week()

        # Fyll tävling/liga-comboboxarna först
        seasons = self.model.get_all_seasons()
        self.view.set_seasons(seasons)

        coupon = self.model.get_by_year_week(
            year,
            week
        )

        # Ingen kupong finns för vald vecka
        if coupon is None:
            self.model.current_coupon = None
            self.view.set_buttons_enabled(False)
            self.view.update_coupon_matches([])

            self.view.add_coupon_button.setEnabled(True)
            self.view.game_table.setEnabled(False)

            return

        # Kupong finns
        self.model.current_coupon = coupon

        self.view.add_coupon_button.setEnabled(False)
        self.view.game_table.setEnabled(True)

        # Visa ligor och resultat
        self.view.update_coupon_matches(
            coupon.soccer_matches
        )

        # Ladda lagen efter att ligan är vald
        for row, coupon_match in enumerate(
            coupon.soccer_matches
        ):
            match = coupon_match.soccer_match

            if match.season_id is None:
                continue

            teams = self.model.get_teams(
                match.season_id
            )

            self.view.set_teams(
                row,
                teams,
                match.home_team.name,
                match.away_team.name
            )

        self.view.set_buttons_enabled(True)

    # Funktion för att rensa formuläret i vyn.
    def clear_form(self):
        self.view.clear_form()
