from PySide6.QtCharts import (QBarCategoryAxis, QBarSeries, QBarSet, QChart,
                              QChartView, QValueAxis)
from PySide6.QtCore import QMargins, QSize, Qt, Signal
from PySide6.QtGui import QGuiApplication, QPainter, QPixmap
from PySide6.QtWidgets import (QCheckBox, QFileDialog, QFrame, QGridLayout,
                               QLabel, QLineEdit, QSpinBox, QStackedWidget,
                               QTableWidgetItem, QWidget)

from misc.base_table_widget import BaseTableWidget
from misc.buttons import (AddButton, BackButton, CopyDiagramButton,
                          DeleteButton, OpenGraphButton, SaveAsImageButton,
                          ShowDetailsButton, ShowOverviewButton)
from misc.combo_boxes.frame_combo_box import FrameComboBox
from misc.combo_boxes.key_combo_box import KeyComboBox
from misc.dialogs.add_bet_dialog import AddBetDialog
from misc.statistic_card import StatisticCard
from mvc import View


class BetView(View):
    """
        Vy för att visa och hantera vad.
    """

    # --------------------------------------------------
    # Signaler
    # --------------------------------------------------

    frame_changed = Signal(int, str)
    key_changed = Signal(int, str)
    math_changed = Signal(int, bool)

    # --------------------------------------------------
    # Kolumner - översiktstabell
    # --------------------------------------------------

    COLUMN_ID = 0
    COLUMN_COUPON = 1
    COLUMN_SYSTEM = 2
    COLUMN_YEAR_WEEK = 3
    COLUMN_CORRECT = 4
    COLUMN_PRIZE = 5

    COLUMN_COUNT = 6

    TABLE_HEADERS = (
        "Id",
        "Kupong",
        "System",
        "Omgång",
        "Antal rätt",
        "Vinst"
    )

    # --------------------------------------------------
    # Kolumner - detaljtabell
    # --------------------------------------------------

    DETAIL_COLUMN_COUNTRY = 0
    DETAIL_COLUMN_HOME_TEAM = 1
    DETAIL_COLUMN_AWAY_TEAM = 2
    DETAIL_COLUMN_MATH = 3
    DETAIL_COLUMN_FRAME = 4
    DETAIL_COLUMN_KEY = 5

    DETAIL_COLUMN_COUNT = 6

    DETAIL_TABLE_HEADERS = (
        "#",
        "Hemmalag",
        "Bortalag",
        "M",
        "Ram",
        "U-tecken"
    )

    # --------------------------------------------------
    # Texter
    # --------------------------------------------------

    VIEW_TITLE = "Vad"
    GRAPH_TITLE = "Statistik"

    # --------------------------------------------------
    # Tabellinställningar
    # --------------------------------------------------

    MINIMUM_COLUMN_WIDTH = 80

    FLAG_WIDTH = 24
    FLAG_HEIGHT = 16

    # --------------------------------------------------
    # Statistikfält
    # --------------------------------------------------

    CORRECT_MIN = 0
    CORRECT_MAX = 13

    PRIZE_MIN = 0
    PRIZE_MAX = 10_000_000

    # --------------------------------------------------
    # Layout
    # --------------------------------------------------

    DETAIL_LAYOUT_SPACING = 12
    GRAPH_LAYOUT_SPACING = 12

    # --------------------------------------------------
    # Ram
    # --------------------------------------------------

    FRAME_OPTIONS_WITH_KEYS = (
        "1X",
        "12",
        "X2",
        "1X2"
    )

    def __init__(self):
        super().__init__()

        self.layout = self.create_layout()

        self.create_header(
            self.VIEW_TITLE
        )

        self.layout.addWidget(
            self.header
        )

        self.stacked_widget = QStackedWidget()

        self.create_overview_widget()
        self.create_detail_widget()
        self.create_graph_widget()

        self.layout.addWidget(self.stacked_widget)
        self.create_bottom_widget()
        self.setLayout(self.layout)

        self.show_overview()

    # --------------------------------------------------
    # Översikt
    # --------------------------------------------------

    def create_overview_widget(self):
        """
            Skapar översikten med tabellen över tidigare vad.
        """
        self.overview_widget = QWidget()

        layout = self.create_vertical_sub_layout(
            parent=self.overview_widget,
            spacing=None
        )

        self.bet_table = BaseTableWidget(
            True,
            True,
            0,
            self.COLUMN_COUNT
        )

        self.bet_table.setHorizontalHeaderLabels(
            self.TABLE_HEADERS
        )

        self.bet_table.set_narrow_columns([
            self.COLUMN_ID,
            self.COLUMN_COUPON,
            self.COLUMN_YEAR_WEEK,
            self.COLUMN_CORRECT,
            self.COLUMN_PRIZE
        ])

        self.bet_table.set_wide_column(
            self.COLUMN_SYSTEM
        )

        layout.addWidget(self.bet_table)
        self.stacked_widget.addWidget(self.overview_widget)

    # --------------------------------------------------
    # Detaljvy
    # --------------------------------------------------

    def create_detail_widget(self):
        """
            Skapar detaljvyn för ett valt vad.
        """
        self.detail_widget = QWidget()

        layout = self.create_vertical_sub_layout(
            parent=self.detail_widget,
            spacing=self.DETAIL_LAYOUT_SPACING
        )

        self.create_detail_info()
        layout.addWidget(self.detail_info_widget)

        self.create_statistic_cards()
        layout.addWidget(self.statistic_widget)

        self.create_detail_table()

        layout.addWidget(
            self.detail_table,
            stretch=1
        )
        self.stacked_widget.addWidget(self.detail_widget)

    def create_detail_info(self):
        """
            Skapar informationsfälten för valt vad.
        """
        self.detail_info_widget = QWidget()

        layout = QGridLayout(self.detail_info_widget)
        layout.setContentsMargins(
            0,
            0,
            0,
            0
        )
        layout.setHorizontalSpacing(15)
        layout.setVerticalSpacing(8)

        self.bet_id_edit = QLineEdit()
        self.bet_id_edit.setReadOnly(True)

        self.year_week_edit = QLineEdit()
        self.year_week_edit.setReadOnly(True)

        self.system_edit = QLineEdit()
        self.system_edit.setReadOnly(True)

        self.correct_edit = QSpinBox()

        self.correct_edit.setRange(
            self.CORRECT_MIN,
            self.CORRECT_MAX
        )

        self.prize_edit = QSpinBox()

        self.prize_edit.setRange(
            self.PRIZE_MIN,
            self.PRIZE_MAX
        )

        self.prize_edit.setSuffix(" kr")
        self.total_cost = QLineEdit()
        self.total_cost.setReadOnly(True)

        layout.addWidget(
            QLabel("Id"),
            0,
            0
        )

        layout.addWidget(
            self.bet_id_edit,
            0,
            1
        )

        layout.addWidget(
            QLabel("Datum"),
            0,
            2
        )

        layout.addWidget(
            self.year_week_edit,
            0,
            3
        )

        layout.addWidget(
            QLabel("System"),
            0,
            4
        )

        layout.addWidget(
            self.system_edit,
            0,
            5
        )

        layout.addWidget(
            QLabel("Antal rätt"),
            1,
            0
        )

        layout.addWidget(
            self.correct_edit,
            1,
            1
        )

        layout.addWidget(
            QLabel("Vinst"),
            1,
            2
        )

        layout.addWidget(
            self.prize_edit,
            1,
            3
        )

        layout.addWidget(
            QLabel("Total kostnad"),
            1,
            4
        )

        layout.addWidget(
            self.total_cost,
            1,
            5
        )

    def create_statistic_cards(self):
        """
            Skapar statistikkorten.
        """
        self.statistic_widget = QWidget()

        layout = self.create_horizontal_sub_layout(
            parent=self.statistic_widget,
            spacing=2
        )

        self.full_card = StatisticCard("Helgarderingar")
        layout.addWidget(self.full_card)

        self.half_card = StatisticCard("Halvgarderingar")

        layout.addWidget(self.half_card)
        self.fixed_card = StatisticCard("Spikar")

        layout.addWidget(self.fixed_card)

    def create_detail_table(self):
        """
            Skapar matchtabellen i detaljvyn.
        """
        self.detail_table = BaseTableWidget(
            False,
            True,
            0,
            self.DETAIL_COLUMN_COUNT
        )

        self.detail_table.setHorizontalHeaderLabels(self.DETAIL_TABLE_HEADERS)
        self.detail_table.set_minimum_column_width(self.MINIMUM_COLUMN_WIDTH)

        self.detail_table.set_wide_columns([
            self.DETAIL_COLUMN_HOME_TEAM,
            self.DETAIL_COLUMN_AWAY_TEAM
        ])

        self.detail_table.set_narrow_columns([
            self.DETAIL_COLUMN_COUNTRY,
            self.DETAIL_COLUMN_MATH,
            self.DETAIL_COLUMN_FRAME,
            self.DETAIL_COLUMN_KEY
        ])

        self.detail_table.setIconSize(
            QSize(
                self.FLAG_WIDTH,
                self.FLAG_HEIGHT
            )
        )

    # --------------------------------------------------
    # Diagram
    # --------------------------------------------------

    def create_graph_widget(self):
        """
            Skapar vyn med statistikdiagram.
        """
        self.graph_widget = QWidget()

        layout = self.create_vertical_sub_layout(
            parent=self.graph_widget,
            spacing=self.GRAPH_LAYOUT_SPACING
        )

        self.chart_view = QChartView()

        self.chart_view.setFrameShape(QFrame.Shape.NoFrame)

        self.chart_view.setStyleSheet("""
            QChartView {
                background-color: white;
                border: none;
            }
        """)

        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chart_view.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        self.chart_view.setAutoFillBackground(True)
        layout.addWidget(self.chart_view)

        self.stacked_widget.addWidget(self.graph_widget)

    def copy_diagram_to_clipboard(self):
        """
            Kopierar diagrammet till urklipp.
        """
        chart = self.chart_view.chart()

        pixmap = QPixmap(self.chart_view.size())
        pixmap.fill(Qt.GlobalColor.white)

        painter = QPainter(pixmap)

        chart.scene().render(painter)

        painter.end()
        QGuiApplication.clipboard().setPixmap(pixmap)

    def save_diagram_as_image(self):
        """
            Sparar diagrammet som bild.
        """
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Spara diagram",
            "diagram.png",
            (
                "PNG-bilder (*.png);;"
                "JPEG-bilder (*.jpg *.jpeg)"
            )
        )

        if not filename:
            return

        pixmap = self.chart_view.grab()
        pixmap.save(filename)

    # --------------------------------------------------
    # Bottenpanel
    # --------------------------------------------------

    def create_bottom_widget(self):
        """
            Skapar den nedre knappraden.
        """
        self.bottom_widget = QWidget()

        layout = self.create_horizontal_sub_layout(
            parent=self.bottom_widget,
            spacing=None
        )

        self.back_from_graph_widget_button = BackButton()
        layout.addWidget(self.back_from_graph_widget_button)

        self.add_bet_button = AddButton()
        layout.addWidget(self.add_bet_button)

        self.open_graph_button = OpenGraphButton()
        layout.addWidget(self.open_graph_button)

        self.show_details_button = ShowDetailsButton()
        layout.addWidget(self.show_details_button)

        self.show_overview_button = ShowOverviewButton()
        layout.addWidget(self.show_overview_button)

        self.copy_diagram_button = CopyDiagramButton()
        layout.addWidget(self.copy_diagram_button)

        self.save_diagram_as_image_button = SaveAsImageButton()
        layout.addWidget(self.save_diagram_as_image_button)

        self.delete_bet_button = DeleteButton()
        layout.addWidget(self.delete_bet_button)

        self.layout.addWidget(self.bottom_widget)

    def set_buttons_enabled(self, status):
        """
            Aktiverar eller inaktiverar knappar
            som kräver ett markerat vad.
        """
        self.delete_bet_button.setEnabled(status)
        self.show_details_button.setEnabled(status)

    # --------------------------------------------------
    # Översiktstabell
    # --------------------------------------------------

    def update_overview_table(self, bets):
        """
            Uppdaterar tabellen med tidigare vad.
        """
        self.bet_table.clearContents()

        self.bet_table.setRowCount(len(bets))

        for row, bet in enumerate(bets):
            values = (
                bet.id,
                bet.coupon.id,
                bet.system.display_name,
                f"{bet.coupon.coupon_year} v.{bet.coupon.coupon_week}",
                (
                    ""
                    if bet.correct_count is None
                    else bet.correct_count
                ),
                (
                    ""
                    if bet.prize is None
                    else f"{bet.prize} kr"
                )
            )

            for column, value in enumerate(values):
                self.bet_table.setItem(
                    row,
                    column,
                    QTableWidgetItem(
                        str(value)
                    )
                )

    # --------------------------------------------------
    # Statistikdiagram
    # --------------------------------------------------

    def update_statistic_graph(
        self,
        data,
        average
    ):
        """
        Uppdaterar diagrammet med statistik
        över antal rätt.
        """
        series = QBarSeries()

        bar_set = QBarSet("Antal rätt")

        categories = []
        max_value = 0

        for item in data:
            correct = str(item["ratt"])

            count = item["antal"]
            categories.append(correct)
            bar_set.append(count)

            max_value = max(
                max_value,
                count
            )

        series.append(bar_set)
        chart = QChart()

        chart.addSeries(series)

        chart.setTitle(
            (
                "Frekvens av antal rätt – "
                f"Genomsnitt: {average:.2f} rätt"
            )
        )

        chart.setTheme(
            QChart.ChartTheme.ChartThemeLight
        )

        chart.setMargins(
            QMargins(
                25,
                25,
                25,
                25
            )
        )

        chart.layout().setContentsMargins(
            20,
            10,
            20,
            20
        )

        chart.setBackgroundBrush(Qt.GlobalColor.white)
        chart.setPlotAreaBackgroundBrush(Qt.GlobalColor.white)
        chart.setBackgroundVisible(True)
        chart.setPlotAreaBackgroundVisible(True)

        axis_x = QBarCategoryAxis()
        axis_x.append(categories)

        axis_x.setLabelsBrush(Qt.GlobalColor.black)
        axis_x.setGridLineVisible(False)

        chart.addAxis(
            axis_x,
            Qt.AlignmentFlag.AlignBottom
        )

        series.attachAxis(axis_x)
        axis_y = QValueAxis()
        axis_y.setLabelFormat("%d")

        axis_y.setRange(
            0,
            max(
                1,
                max_value
            )
        )

        axis_y.setTickCount(
            max(
                2,
                max_value + 1
            )
        )

        axis_y.setLabelsBrush(Qt.GlobalColor.black)
        axis_y.setGridLineColor(Qt.GlobalColor.lightGray)

        chart.addAxis(
            axis_y,
            Qt.AlignmentFlag.AlignLeft
        )

        series.attachAxis(axis_y)

        chart.legend().setVisible(False)
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.chart_view.setChart(chart)

    # --------------------------------------------------
    # Information om vad
    # --------------------------------------------------

    def update_bet_info(self, bet):
        """
            Uppdaterar informationen om valt vad.
        """
        self.bet_id_edit.setText(
            str(bet.id)
        )

        self.year_week_edit.setText(
            f"{bet.coupon.coupon_year} v.{bet.coupon.coupon_week}"
        )

        self.system_edit.setText(bet.system.display_name)
        self.block_bet_edit_signals(True)

        self.correct_edit.setValue(
            0
            if bet.correct_count is None
            else bet.correct_count
        )

        self.prize_edit.setValue(
            0
            if bet.prize is None
            else bet.prize
        )

        self.total_cost.setText(
            "0 kr"
            if bet.total_cost is None
            else f"{bet.total_cost} kr"
        )

        self.block_bet_edit_signals(False)

    # --------------------------------------------------
    # Detaljtabell
    # --------------------------------------------------

    def update_detail_table(
        self,
        coupon_matches,
        bet_details=None,
        validator=None
    ):
        """
            Uppdaterar detaljtabellen för valt vad.
        """
        self.detail_table.clearContents()
        self.detail_table.setRowCount(len(coupon_matches))

        details = {}

        if bet_details:
            for detail in bet_details:
                details[detail.match_number] = {
                    "frame": detail.frame_value,
                    "key": detail.key_value,
                    "math": detail.mathematical_value
                }

        for row, coupon_match in enumerate(
            coupon_matches
        ):
            detail = details.get(
                row + 1,
                {}
            )

            saved_frame = detail.get(
                "frame",
                ""
            )

            saved_math = detail.get(
                "math",
                False
            )

            saved_key = detail.get(
                "key",
                ""
            )

            match = coupon_match.soccer_match

            self.detail_table.setCellWidget(
                row,
                self.DETAIL_COLUMN_COUNTRY,
                self.create_flag_widget(
                    match.season.competition
                )
            )

            self.detail_table.setItem(
                row,
                self.DETAIL_COLUMN_HOME_TEAM,
                QTableWidgetItem(
                    match.home_team.display_name
                )
            )

            self.detail_table.setItem(
                row,
                self.DETAIL_COLUMN_AWAY_TEAM,
                QTableWidgetItem(
                    match.away_team.display_name
                )
            )

            math_checkbox = QCheckBox()
            math_checkbox.setChecked(saved_math)

            math_checkbox.setEnabled(
                saved_frame
                in self.FRAME_OPTIONS_WITH_KEYS
            )

            math_checkbox.toggled.connect(
                lambda checked, r=row:
                self.math_changed.emit(
                    r + 1,
                    checked
                )
            )

            self.detail_table.setCellWidget(
                row,
                self.DETAIL_COLUMN_MATH,
                math_checkbox
            )

            if validator:
                frame_values = (
                    validator
                    .get_allowed_frame_values(row)
                )
            else:
                frame_values = None

            frame_combo = FrameComboBox(frame_values)

            index = frame_combo.findText(saved_frame)

            if index >= 0:
                frame_combo.setCurrentIndex(
                    index
                )

            frame_combo.currentTextChanged.connect(
                lambda value,
                r=row,
                checkbox=math_checkbox:
                (
                    self.update_math_checkbox(
                        checkbox,
                        value
                    ),
                    self.frame_changed.emit(
                        r + 1,
                        value
                    )
                )
            )

            self.detail_table.setCellWidget(
                row,
                self.DETAIL_COLUMN_FRAME,
                frame_combo
            )

            has_key = (
                saved_frame
                in self.FRAME_OPTIONS_WITH_KEYS
            )

            if (
                validator
                and has_key
                and not saved_math
            ):
                key_values = (
                    validator
                    .get_allowed_key_values(row)
                )
            else:
                key_values = [""]

            key_combo = KeyComboBox(key_values)

            index = key_combo.findText(saved_key)

            if index >= 0:
                key_combo.setCurrentIndex(
                    index
                )

            key_combo.setEnabled(
                has_key
                and not saved_math
            )

            key_combo.currentTextChanged.connect(
                lambda value, r=row:
                self.key_changed.emit(
                    r + 1,
                    value
                )
            )

            self.detail_table.setCellWidget(
                row,
                self.DETAIL_COLUMN_KEY,
                key_combo
            )

        self.detail_table.center_icon_column(self.DETAIL_COLUMN_COUNTRY)

        self.detail_table.set_columns_readonly([
            self.DETAIL_COLUMN_HOME_TEAM,
            self.DETAIL_COLUMN_AWAY_TEAM
        ])

    # --------------------------------------------------
    # Statistik
    # --------------------------------------------------

    def update_system_statistics(
        self,
        statistics
    ):
        """
            Uppdaterar statistikkorten.
        """
        self.full_card.update_values(
            statistics["full"],
            (
                statistics["full"]
                + statistics["full_left"]
            )
        )

        self.half_card.update_values(
            statistics["half"],
            (
                statistics["half"]
                + statistics["half_left"]
            )
        )

        self.fixed_card.update_values(
            statistics["fixed"],
            (
                statistics["fixed"]
                + statistics["fixed_left"]
            )
        )

    # --------------------------------------------------
    # Navigering
    # --------------------------------------------------

    def show_overview(self):
        """
            Visar översikten.
        """
        self.header.show()

        self.update_header_text(self.VIEW_TITLE)

        self.set_button_visibility(
            show_details_button=True,
            open_graph_button=True,
            add_bet_button=True,
            delete_bet_button=True
        )

        self.stacked_widget.setCurrentWidget(self.overview_widget)

    def show_details(self):
        """
            Visar detaljvyn.
        """
        self.header.hide()
        self.set_button_visibility(show_overview_button=True)
        self.stacked_widget.setCurrentWidget(self.detail_widget)

    def show_graph_widget(self):
        """
            Visar diagramvyn.
        """
        self.update_header_text(self.GRAPH_TITLE)
        self.header.show()

        self.set_button_visibility(
            back_from_graph_widget_button=True,
            copy_diagram_button=True,
            save_diagram_as_image_button=True
        )

        self.stacked_widget.setCurrentWidget(self.graph_widget)

    # --------------------------------------------------
    # Tabellval
    # --------------------------------------------------

    def get_active_selection_table(self):
        """
            Returnerar den tabell som för närvarande
            används för markering.
        """
        current_widget = (self.stacked_widget.currentWidget())

        if current_widget == self.overview_widget:
            return self.bet_table

        if current_widget == self.detail_widget:
            return self.detail_table

        return None

    def show_key_row_column(
        self,
        visible=True
    ):
        """
            Visar eller döljer kolumnen med U-tecken.
        """
        self.detail_table.setColumnHidden(
            self.DETAIL_COLUMN_KEY,
            not visible
        )

    # --------------------------------------------------
    # Comboboxar
    # --------------------------------------------------

    def refresh_frame_combos(
        self,
        validator
    ):
        """
            Uppdaterar alla ram-comboboxar.
        """
        for row in range(
            self.detail_table.rowCount()
        ):
            combo = self.detail_table.cellWidget(
                row,
                self.DETAIL_COLUMN_FRAME
            )

            if combo:
                current = combo.currentText()

                values = (validator.get_allowed_frame_values(row))

                self.update_combo_items(
                    combo,
                    values,
                    current
                )

    def refresh_key_combos(
        self,
        validator
    ):
        """
            Uppdaterar alla U-tecken-comboboxar.
        """
        for row in range(
            self.detail_table.rowCount()
        ):
            combo = self.detail_table.cellWidget(
                row,
                self.DETAIL_COLUMN_KEY
            )

            if combo is None:
                continue

            frame_combo = self.detail_table.cellWidget(
                row,
                self.DETAIL_COLUMN_FRAME
            )

            math_checkbox = self.detail_table.cellWidget(
                row,
                self.DETAIL_COLUMN_MATH
            )

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

            if (
                frame in self.FRAME_OPTIONS_WITH_KEYS
                and not is_math
            ):
                current = combo.currentText()

                values = (
                    validator
                    .get_allowed_key_values(row)
                )

                self.update_combo_items(
                    combo,
                    values,
                    current
                )

                combo.setEnabled(True)

            else:
                combo.clear()
                combo.addItem("")

                combo.setEnabled(False)

    def update_math_checkbox(
        self,
        checkbox,
        frame
    ):
        """
            Uppdaterar status för checkboxen
            för matematisk gardering.
        """
        enabled = (
            frame
            in self.FRAME_OPTIONS_WITH_KEYS
        )

        checkbox.setEnabled(enabled)

        if not enabled:
            checkbox.blockSignals(True)
            checkbox.setChecked(False)
            checkbox.blockSignals(False)

    def update_combo_items(
        self,
        combo,
        values,
        current
    ):
        """
            Uppdaterar innehållet i en combobox.
        """
        combo.blockSignals(True)

        combo.clear()
        combo.addItems(values)
        index = combo.findText(current)

        if index >= 0:
            combo.setCurrentIndex(index)

        combo.blockSignals(False)

    # --------------------------------------------------
    # Rensning
    # --------------------------------------------------

    def clear_bet_info(self):
        """
            Rensar informationen om valt vad.
        """
        self.bet_id_edit.clear()
        self.year_week_edit.clear()
        self.system_edit.clear()
        self.total_cost.clear()

        self.block_bet_edit_signals(True)

        self.correct_edit.setValue(0)
        self.prize_edit.setValue(0)

        self.block_bet_edit_signals(False)

        self.bet_table.clearSelection()
        self.detail_table.clearSelection()

    # --------------------------------------------------
    # Flagga
    # --------------------------------------------------

    def create_flag_widget(
        self,
        competition
    ):
        """
            Skapar en centrerad flaggwidget.
        """
        label = QLabel()

        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if competition is None:
            return label

        country = competition.country

        pixmap = QPixmap(country.flag_path)

        if not pixmap.isNull():
            label.setPixmap(
                pixmap.scaled(
                    self.FLAG_WIDTH,
                    self.FLAG_HEIGHT,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )

        label.setToolTip(country.country_name)

        return label

    # --------------------------------------------------
    # Signaler
    # --------------------------------------------------

    def block_bet_edit_signals(
        self,
        blocked
    ):
        """
            Blockerar eller aktiverar signaler
            från redigeringsfälten.
        """
        self.correct_edit.blockSignals(blocked)
        self.prize_edit.blockSignals(blocked)

    # --------------------------------------------------
    # Knappar
    # --------------------------------------------------

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
        """
            Styr vilka knappar som visas.
        """
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

    # --------------------------------------------------
    # Dialoger
    # --------------------------------------------------

    def show_add_bet_dialog(self, coupons, systems):
        """
            Visar dialogen för att lägga till ett vad.
        """

        dialog = AddBetDialog(
            coupons=coupons,
            systems=systems,
            parent=self
        )

        if not dialog.exec():
            return None

        return (
            dialog.coupon_id,
            dialog.system_id,
            dialog.date
        )

    def update_bet_result_row(
        self,
        row,
        correct_count,
        prize
    ):
        """
            Uppdaterar resultat och vinst för en rad.
        """
        self.bet_table.setItem(
            row,
            self.COLUMN_CORRECT,
            QTableWidgetItem(
                str(correct_count)
            )
        )

        self.bet_table.setItem(
            row,
            self.COLUMN_PRIZE,
            QTableWidgetItem(
                f"{prize} kr"
            )
        )
