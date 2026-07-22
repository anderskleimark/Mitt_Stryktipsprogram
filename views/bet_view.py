from PySide6.QtCharts import (QBarCategoryAxis, QBarSeries, QBarSet, QChart,
                              QChartView, QValueAxis)
from PySide6.QtCore import QMargins, QSize, Qt, Signal
from PySide6.QtGui import QGuiApplication, QPainter, QPixmap
from PySide6.QtWidgets import (QCheckBox, QFileDialog, QFrame, QGridLayout,
                               QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QSpinBox, QStackedWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget)

from misc.base_table_widget import BaseTableWidget
from misc.country import Country
from misc.frame_combo_box import FrameComboBox
from misc.key_combo_box import KeyComboBox
from misc.statistic_card import StatisticCard
from mvc import View

# Klass (vy) som visar alla tillagda vad.


class BetView(View):

    # Signal om ramen ändras i någon av matcherna.
    frame_changed = Signal(int, str)
    # Signal som används när någon match får ett U-tecken ändrat.
    key_changed = Signal(int, str)
    # Signal som används när en match ändras gällande matematisk gardering.
    math_changed = Signal(int, bool)

    # Konstanter
    COUNTRY_COLUMN = 0
    HOME_TEAM_COLUMN = 1
    AWAY_TEAM_COLUMN = 2
    MATH_COLUMN = 3
    FRAME_COLUMN = 4
    KEY_COLUMN = 5

    BET_ID_COLUMN = 0
    COUPON_COLUMN = 1
    SYSTEM_COLUMN = 2
    YEAR_WEEK_COLUMN = 3
    CORRECT_COLUMN = 4
    PRIZE_COLUMN = 5

    BET_COLUMNS = 6
    DETAIL_COLUMNS = 6
    MINIMUM_COLUMN_WIDTH = 80

    FRAME_OPTIONS_WITH_KEYS = (
        "1X",
        "12",
        "X2",
        "1X2"
    )

    def __init__(self):
        super().__init__()

        self.bet_id_edit = None
        self.year_week_edit = None
        self.system_edit = None
        self.correct_edit = None
        self.prize_edit = None
        self.total_cost = None
        self.full_card = None
        self.half_card = None
        self.fixed_card = None
        self.detail_table = None

        self.layout = self.create_layout()
        self.create_header("Vad")
        self.layout.addWidget(self.header)

        # Innehållsväxling
        self.stacked_widget = QStackedWidget()
        self.create_overview_table()
        self.create_detail_view()
        self.create_graph_widget()

        self.stacked_widget.addWidget(self.bet_table)
        self.stacked_widget.addWidget(self.detail_widget)
        self.stacked_widget.addWidget(self.graph_widget)
        self.layout.addWidget(self.stacked_widget)

        # Knappar längst ned
        self.create_bottom_widget()
        self.setLayout(self.layout)

        self.show_overview()

    # Funktion som skapar tabellen med de tidigare vaden.
    def create_overview_table(self):

        self.bet_table = BaseTableWidget(True, True, 0, self.BET_COLUMNS)
        self.bet_table.setHorizontalHeaderLabels([
            "Id",
            "Kupong",
            "System",
            "Omgång",
            "Antal rätt",
            "Vinst"
        ])

        self.bet_table.set_narrow_columns(
            [
                self.BET_ID_COLUMN,
                self.COUPON_COLUMN,
                self.YEAR_WEEK_COLUMN,
                self.CORRECT_COLUMN,
                self.PRIZE_COLUMN
            ]
        )
        self.bet_table.set_wide_column(self.SYSTEM_COLUMN)

    # Funktion som skapar den QWidget med detaljer om ett valt vad.
    def create_detail_view(self):
        self.detail_widget = QWidget()

        # Layout
        layout = QVBoxLayout(self.detail_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        # Widgetar
        layout.addWidget(self.create_detail_info())
        layout.addWidget(self.create_statistic_cards())
        layout.addWidget(self.create_detail_table(), stretch=1)

    # Funktion som skapar den översta widgeten i detaljvyn.
    def create_detail_info(self):
        # Information
        info_widget = QWidget()
        grid = QGridLayout(info_widget)

        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(15)
        grid.setVerticalSpacing(8)

        self.bet_id_edit = QLineEdit()
        self.bet_id_edit.setReadOnly(True)

        self.year_week_edit = QLineEdit()
        self.year_week_edit.setReadOnly(True)

        self.system_edit = QLineEdit()
        self.system_edit.setReadOnly(True)

        self.correct_edit = QSpinBox()
        self.correct_edit.setRange(0, 13)

        self.prize_edit = QSpinBox()
        self.prize_edit.setRange(0, 10_000_000)
        self.prize_edit.setSuffix(" kr")

        self.total_cost = QLineEdit()
        self.total_cost.setReadOnly(True)

        grid.addWidget(QLabel("Id"), 0, 0)
        grid.addWidget(self.bet_id_edit, 0, 1)

        grid.addWidget(QLabel("Datum"), 0, 2)
        grid.addWidget(self.year_week_edit, 0, 3)

        grid.addWidget(QLabel("System"), 0, 4)
        grid.addWidget(self.system_edit, 0, 5)

        grid.addWidget(QLabel("Antal rätt"), 1, 0)
        grid.addWidget(self.correct_edit, 1, 1)

        grid.addWidget(QLabel("Vinst"), 1, 2)
        grid.addWidget(self.prize_edit, 1, 3)

        grid.addWidget(QLabel("Total kostnad"), 1, 4)
        grid.addWidget(self.total_cost, 1, 5)

        return info_widget

    # Funktion som skapar statistik-kort i detaljvyn.
    def create_statistic_cards(self):
        # Statistikkort
        cards_widget = QWidget()

        cards_layout = QHBoxLayout(cards_widget)
        cards_layout.setContentsMargins(0, 5, 0, 5)
        cards_layout.setSpacing(2)

        self.full_card = StatisticCard("Helgarderingar")
        self.half_card = StatisticCard("Halvgarderingar")
        self.fixed_card = StatisticCard("Spikar")

        cards_layout.addWidget(self.full_card)
        cards_layout.addWidget(self.half_card)
        cards_layout.addWidget(self.fixed_card)

        return cards_widget

    # Funktion som skapar tabellen i detaljvyn.
    def create_detail_table(self):
        # Matchtabell
        self.detail_table = BaseTableWidget()
        self.detail_table.setColumnCount(self.DETAIL_COLUMNS)
        self.detail_table.setHorizontalHeaderLabels(
            [
                "#",
                "Hemmalag",
                "Bortalag",
                "M",
                "Ram",
                "U-tecken"
            ]
        )

        self.detail_table.set_minimum_column_width(self.MINIMUM_COLUMN_WIDTH)
        self.detail_table.set_wide_columns(
            [self.HOME_TEAM_COLUMN, self.AWAY_TEAM_COLUMN])

        self.detail_table.set_narrow_columns(
            [self.COUNTRY_COLUMN, self.MATH_COLUMN, self.FRAME_COLUMN, self.KEY_COLUMN])

        self.detail_table.setIconSize(QSize(24, 16))

        return self.detail_table

    # Funktion som skapar diagrammet.
    def create_graph_widget(self):
        self.graph_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.chart_view = QChartView()
        self.chart_view.setFrameShape(QFrame.NoFrame)

        self.chart_view.setStyleSheet("""
            QChartView {
                background-color: white;
                border: none;
            }
        """)

        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setRenderHint(QPainter.TextAntialiasing)
        self.chart_view.setAutoFillBackground(True)

        layout.addWidget(self.chart_view)
        self.graph_widget.setLayout(layout)

    # Funktion som kopierar diagrammet till "clipboard".
    def copy_diagram_to_clipboard(self):
        chart = self.chart_view.chart()

        pixmap = QPixmap(self.chart_view.size())
        pixmap.fill(Qt.white)

        painter = QPainter(pixmap)
        chart.scene().render(painter)
        painter.end()

        QGuiApplication.clipboard().setPixmap(pixmap)

    # Funktion som sparar diagrammet som en bild.
    def save_diagram_as_image(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Spara diagram", "diagram.png", "PNG-bilder (*.png);;JPEG-bilder (*.jpg *.jpeg)")

        if not filename:
            return

        pixmap = self.chart_view.grab()
        pixmap.save(filename)

    # Funktion som skapar den QWidget, som finns längst ned. Den innehåller flera knappar med val.
    def create_bottom_widget(self):
        bottom_widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(10)

        # Knappar
        self.back_from_graph_widget_button = QPushButton("Tillbaka")
        self.add_bet_button = QPushButton("Lägg till")
        self.open_graph_button = QPushButton("Öppna graf")
        self.show_details_button = QPushButton("Visa detaljer")
        self.show_overview_button = QPushButton("Visa översikt")
        self.copy_diagram_button = QPushButton("Kopiera diagram")
        self.save_diagram_as_image_button = QPushButton("Spara som bild")
        self.delete_bet_button = QPushButton("Radera")
        self.delete_bet_button.setProperty("buttonClass", "warning")
        buttons = [
            self.back_from_graph_widget_button,
            self.add_bet_button,
            self.open_graph_button,
            self.show_details_button,
            self.show_overview_button,
            self.copy_diagram_button,
            self.save_diagram_as_image_button,
            self.delete_bet_button
        ]
        for button in buttons:
            layout.addWidget(button)
        self.set_buttons_enabled(False)

        # Layout
        bottom_widget.setLayout(layout)
        self.layout.addWidget(bottom_widget)

    # Funktion för att aktivera/deaktivera knappar.
    def set_buttons_enabled(self, status):
        self.delete_bet_button.setEnabled(status)
        self.show_details_button.setEnabled(status)

    # Funktion för att uppdatera tabellen med vad.
    def update_overview_table(self, bets):
        self.bet_table.clearContents()
        self.bet_table.setRowCount(len(bets))

        for row, bet in enumerate(bets):
            self.bet_table.setItem(
                row, self.BET_ID_COLUMN, QTableWidgetItem(str(bet.id)))
            self.bet_table.setItem(
                row, self.COUPON_COLUMN, QTableWidgetItem(str(bet.coupon.id)))
            self.bet_table.setItem(row, self.SYSTEM_COLUMN, QTableWidgetItem(
                str(bet.system.display_name)))

            self.bet_table.setItem(row, self.YEAR_WEEK_COLUMN,
                                   QTableWidgetItem(f"{bet.coupon.year} v.{bet.coupon.week}"))
            self.bet_table.setItem(row, self.CORRECT_COLUMN, QTableWidgetItem(
                "" if bet.correct_count is None else str(bet.correct_count)))
            self.bet_table.setItem(row, self.PRIZE_COLUMN, QTableWidgetItem(
                "" if bet.prize is None else f"{bet.prize} kr"))

    # Funktion som uppdaterar diagrammet.
    def update_statistic_graph(self, data, average):
        series = QBarSeries()
        bar_set = QBarSet("Antal rätt")

        categories = []
        max_value = 0

        for item in data:
            r = str(item["ratt"])
            v = item["antal"]

            categories.append(r)
            bar_set.append(v)

            max_value = max(max_value, v)

        series.append(bar_set)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(
            f"Frekvens av antal rätt – Genomsnitt: {average:.2f} rätt")

        # Ställ in att diagrammet är ljust.
        chart.setTheme(QChart.ChartThemeLight)

        # Lägg till luft.
        chart.setMargins(QMargins(25, 25, 25, 25))
        chart.layout().setContentsMargins(20, 10, 20, 20)

        # Fix av bakgrunden.
        chart.setBackgroundBrush(Qt.white)
        chart.setPlotAreaBackgroundBrush(Qt.white)
        chart.setBackgroundVisible(True)
        chart.setPlotAreaBackgroundVisible(True)

        # X-axeln
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        axis_x.setLabelsBrush(Qt.black)
        axis_x.setGridLineVisible(False)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)

        # Y-axeln
        axis_y = QValueAxis()
        axis_y.setLabelFormat("%d")
        axis_y.setRange(0, max(1, max_value))
        axis_y.setTickCount(max(2, max_value + 1))
        axis_y.setLabelsBrush(Qt.black)
        axis_y.setGridLineColor(Qt.lightGray)
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)

        chart.legend().setVisible(False)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart_view.setChart(chart)

    # Funktion som uppdaterar detaljerna om det valda vadet.
    def update_bet_info(self, bet):
        self.bet_id_edit.setText(str(bet.id))
        self.year_week_edit.setText(f"{bet.coupon.year} v.{bet.coupon.week}")
        self.system_edit.setText(bet.system.display_name)

        # Blockera signaler så att autosparning inte triggas
        self.block_bet_edit_signals(True)

        self.correct_edit.setValue(
            0 if bet.correct_count is None else bet.correct_count)
        self.prize_edit.setValue(0 if bet.prize is None else bet.prize)

        self.total_cost.setText(
            "0 kr" if bet.total_cost is None else f"{bet.total_cost} kr"
        )

        self.block_bet_edit_signals(False)

    # Funktion för att uppdatera tabellen med detaljer.
    def update_detail_table(
        self,
        coupon_matches,
        bet_details=None,
        validator=None
    ):
        self.detail_table.clearContents()
        self.detail_table.setRowCount(len(coupon_matches))

        details = {}

        if bet_details:
            for detail in bet_details:
                details[detail.match_number] = {
                    "frame": detail.frame_value,
                    "key": detail.key_value,
                    "math": detail.mathematical
                }

        for row, coupon_match in enumerate(coupon_matches):
            detail = details.get(row + 1, {})
            saved_frame = detail.get("frame", "")
            saved_math = detail.get("math", False)
            saved_key = detail.get("key", "")

            # Landsflagga
            self.detail_table.setCellWidget(
                row,
                self.COUNTRY_COLUMN,
                self.create_flag_widget(
                    coupon_match.soccer_match.competition
                )
            )

            # Hemmalag
            self.detail_table.setItem(
                row,
                self.HOME_TEAM_COLUMN,
                QTableWidgetItem(
                    coupon_match.soccer_match.home_team.name
                )
            )

            # Bortalag
            self.detail_table.setItem(
                row,
                self.AWAY_TEAM_COLUMN,
                QTableWidgetItem(
                    coupon_match.soccer_match.away_team.name
                )
            )

            # M-checkbox
            m_checkbox = QCheckBox()
            m_checkbox.setChecked(saved_math)

            m_checkbox.setEnabled(
                saved_frame in self.FRAME_OPTIONS_WITH_KEYS
            )

            m_checkbox.toggled.connect(
                lambda checked, r=row:
                    self.math_changed.emit(r + 1, checked)
            )

            self.detail_table.setCellWidget(
                row,
                self.MATH_COLUMN,
                m_checkbox
            )

            # Ram-combobox
            if validator:
                frame_values = validator.get_allowed_frame_values(row)
            else:
                frame_values = None

            frame_combo = FrameComboBox(frame_values)
            index = frame_combo.findText(saved_frame)

            if index >= 0:
                frame_combo.setCurrentIndex(index)

            frame_combo.currentTextChanged.connect(
                lambda value, r=row, cb=m_checkbox:
                    (
                        self.update_math_checkbox(cb, value),
                        self.frame_changed.emit(r + 1, value)
                    )
            )

            self.detail_table.setCellWidget(
                row,
                self.FRAME_COLUMN,
                frame_combo
            )

            # U-tecken-combobox
            has_key = saved_frame in self.FRAME_OPTIONS_WITH_KEYS

            if (
                validator
                and has_key
                and not saved_math
            ):
                key_values = validator.get_allowed_key_values(row)
            else:
                key_values = [""]

            key_combo = KeyComboBox(key_values)
            saved_key = details.get(row + 1, {}).get("key", "")
            index = key_combo.findText(saved_key)

            if index >= 0:
                key_combo.setCurrentIndex(index)

            key_combo.setEnabled(
                has_key and not saved_math
            )

            key_combo.currentTextChanged.connect(
                lambda value, r=row:
                    self.key_changed.emit(r + 1, value)
            )

            self.detail_table.setCellWidget(
                row,
                self.KEY_COLUMN,
                key_combo
            )

        self.detail_table.center_icon_column(self.COUNTRY_COLUMN)
        self.detail_table.set_columns_readonly(
            [self.HOME_TEAM_COLUMN, self.AWAY_TEAM_COLUMN])

    # Funktion som visar återstående garderingar.
    def update_system_statistics(self, statistics):
        self.full_card.update_values(
            statistics["full"], statistics["full"] + statistics["full_left"])
        self.half_card.update_values(
            statistics["half"], statistics["half"] + statistics["half_left"])

        self.fixed_card.update_values(
            statistics["fixed"], statistics["fixed"] + statistics["fixed_left"])

    # Funktion för att visa översikten med de olika vaden.
    def show_overview(self):
        self.header.show()
        self.set_button_visibility(
            show_details_button=True,
            open_graph_button=True,
            add_bet_button=True,
            delete_bet_button=True

        )
        self.stacked_widget.setCurrentWidget(self.bet_table)

    # Funktion för att visa vyn med detaljer om ett valt vad.
    def show_details(self):
        self.header.hide()
        self.set_button_visibility(
            show_overview_button=True
        )
        self.stacked_widget.setCurrentWidget(self.detail_widget)

    # Funktion som visar grafen med stapeldiagrammet.
    def show_graph_widget(self):
        self.header.setText("Statistik")
        self.header.show()
        self.set_button_visibility(
            back_from_graph_widget_button=True,
            copy_diagram_button=True,
            save_diagram_as_image_button=True
        )
        self.stacked_widget.setCurrentWidget(self.graph_widget)

    # Funktion som visar/döljer kolumnen med U-tecken.abs
    def show_key_row_column(self, visible=True):
        self.detail_table.setColumnHidden(self.KEY_COLUMN, not visible)

    # Superfunktion, som behövs för att rensa markering, om man klickar utanför tabellen.
    def get_active_selection_table(self):
        if self.stacked_widget.currentWidget() == self.bet_table:
            return self.bet_table

        return self.detail_table

    # Funktion som uppdaterar tillåtna ramtecken i alla comboboxar.
    def refresh_frame_combos(self, validator):
        for row in range(
            self.detail_table.rowCount()
        ):
            combo = self.detail_table.cellWidget(
                row,
                self.FRAME_COLUMN
            )

            if combo:
                current = combo.currentText()

                values = validator.get_allowed_frame_values(row)
                self.update_combo_items(combo, values, current)

    def refresh_key_combos(self, validator):
        for row in range(self.detail_table.rowCount()):
            combo = self.detail_table.cellWidget(row, self.KEY_COLUMN)

            if combo:
                frame_combo = self.detail_table.cellWidget(
                    row, self.FRAME_COLUMN)
                math_checkbox = self.detail_table.cellWidget(
                    row, self.MATH_COLUMN)

                frame = (
                    frame_combo.currentText()
                    if frame_combo
                    else ""
                )

                is_math = (
                    math_checkbox.isChecked()
                    if math_checkbox
                    else False
                )

                # U-tecken får endast användas på halv- och helgarderingar
                # och inte på matematiska garderingar.
                if (
                    frame in self.FRAME_OPTIONS_WITH_KEYS
                    and not is_math
                ):
                    current = combo.currentText()
                    values = validator.get_allowed_key_values(row)
                    self.update_combo_items(combo, values, current)
                    combo.setEnabled(True)

                else:
                    combo.clear()
                    combo.addItem("")
                    combo.setEnabled(False)

    def update_math_checkbox(self, checkbox, frame):
        enabled = frame in self.FRAME_OPTIONS_WITH_KEYS
        checkbox.setEnabled(enabled)

        if not enabled:
            checkbox.blockSignals(True)
            checkbox.setChecked(False)
            checkbox.blockSignals(False)

    # Funktion som rensar detaljinformation om ett visst vad.
    def clear_bet_info(self):
        self.bet_id_edit.clear()
        self.year_week_edit.clear()
        self.system_edit.clear()
        self.block_bet_edit_signals(True)

        self.correct_edit.setValue(0)
        self.prize_edit.setValue(0)

        self.block_bet_edit_signals(False)

        self.bet_table.clearSelection()
        self.detail_table.clearSelection()

    # Funktion som används för att skapa en flagga.
    def create_flag_widget(self, competition):
        country = competition.country if competition else ""

        label = QLabel()
        label.setAlignment(Qt.AlignCenter)

        pixmap = QPixmap(
            Country.get_flag_path(country)
        )

        if not pixmap.isNull():
            label.setPixmap(
                pixmap.scaled(
                    24,
                    16,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )

        label.setToolTip(country)

        return label

    # Funktion för att blockera eller avblockera signaler.
    def block_bet_edit_signals(self, blocked):
        self.correct_edit.blockSignals(blocked)
        self.prize_edit.blockSignals(blocked)

    # Funktion för att uppdatera combo-boxar.
    def update_combo_items(self, combo, values, current):
        combo.blockSignals(True)

        combo.clear()
        combo.addItems(values)

        index = combo.findText(current)
        if index >= 0:
            combo.setCurrentIndex(index)

        combo.blockSignals(False)

    # Funktion för att sätta olika knappars synlighet.
    def set_button_visibility(
        self,
        *,
        show_details_button=False,
        show_overview_button=False,
        open_graph_button=False,
        back_from_graph_widget_button=False,
        add_bet_button=False,
        delete_bet_button=False,
        copy_diagram_button=False,
        save_diagram_as_image_button=False
    ):
        self.show_details_button.setVisible(show_details_button)
        self.show_overview_button.setVisible(show_overview_button)
        self.open_graph_button.setVisible(open_graph_button)
        self.back_from_graph_widget_button.setVisible(
            back_from_graph_widget_button)
        self.add_bet_button.setVisible(add_bet_button)
        self.delete_bet_button.setVisible(delete_bet_button)
        self.copy_diagram_button.setVisible(copy_diagram_button)
        self.save_diagram_as_image_button.setVisible(
            save_diagram_as_image_button)
