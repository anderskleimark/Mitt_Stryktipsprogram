from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QCheckBox, QLabel, QLineEdit, QSpinBox,
                               QTableWidgetItem, QWidget)

from misc.base_table_widget import BaseTableWidget
from misc.combo_boxes.frame_combo_box import FrameComboBox
from misc.combo_boxes.key_combo_box import KeyComboBox
from misc.statistic_card import StatisticCard

from widgets.base_widget import BaseWidget


class BetDetailWidget(BaseWidget):
    # Signaler
    bet_result_changed = Signal()
    key_changed = Signal(int, str)
    frame_changed = Signal(int, str)
    math_changed = Signal(int, bool)

    # Mellanrum
    HORIZONTAL_SPACING = 15
    VERTICAL_SPACING = 8

    # Kolumner - detaljtabell
    COLUMN_COUNTRY = 0
    COLUMN_HOME_TEAM = 1
    COLUMN_AWAY_TEAM = 2
    COLUMN_MATH = 3
    COLUMN_FRAME = 4
    COLUMN_KEY = 5
    COLUMN_COUNT = 6

    # Statistikfält
    CORRECT_MIN = 0
    CORRECT_MAX = 13

    PRIZE_MIN = 0
    PRIZE_MAX = 10_000_000

    TABLE_HEADERS = (
        "#",
        "Hemmalag",
        "Bortalag",
        "M",
        "Ram",
        "U-tecken"
    )

    # Tabellinställningar
    MINIMUM_COLUMN_WIDTH = 80

    FLAG_WIDTH = 24
    FLAG_HEIGHT = 16

    FRAME_OPTIONS_WITH_KEYS = (
        "1X",
        "12",
        "X2",
        "1X2"
    )

    def __init__(self):
        super().__init__()
        self._build_widget()
        self._setup_signals()

    def _setup_signals(self):
        """
            Kopplar widgetens interna signaler.
        """
        self.correct_edit.valueChanged.connect(
            lambda _: self.bet_result_changed.emit()
        )

        self.prize_edit.valueChanged.connect(
            lambda _: self.bet_result_changed.emit()
        )

    def _build_widget(self):
        layout = self.create_vertical_layout(
            parent=self,
            spacing=self.SPACING
        )

        self._create_detail_info()
        layout.addWidget(self.detail_info_widget)

        self._create_statistic_cards()
        layout.addWidget(self.statistic_widget)

        self._create_table()

        layout.addWidget(
            self.table,
            stretch=1
        )

    def _create_detail_info(self):
        """
            Skapar informationsfälten för valt vad.
        """
        self.detail_info_widget = QWidget()

        layout = self.create_grid_layout(
            parent=self.detail_info_widget,
            horizontal_spacing=self.HORIZONTAL_SPACING,
            vertical_spacing=self.VERTICAL_SPACING
        )

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

    def _create_statistic_cards(self):
        """
            Skapar statistikkorten.
        """
        self.statistic_widget = QWidget()

        layout = self.create_horizontal_layout(
            parent=self.statistic_widget,
            spacing=2
        )

        self.full_card = StatisticCard("Helgarderingar")
        layout.addWidget(self.full_card)

        self.half_card = StatisticCard("Halvgarderingar")
        layout.addWidget(self.half_card)

        self.fixed_card = StatisticCard("Spikar")
        layout.addWidget(self.fixed_card)

    def _create_table(self):
        """
            Skapar matchtabellen.
        """
        self.table = BaseTableWidget(
            False,
            True,
            self.COLUMN_COUNT
        )

        self.table.setHorizontalHeaderLabels(self.TABLE_HEADERS)
        self.table.set_minimum_column_width(self.MINIMUM_COLUMN_WIDTH)

        self.table.set_wide_columns([
            self.COLUMN_HOME_TEAM,
            self.COLUMN_AWAY_TEAM
        ])

        self.table.set_narrow_columns([
            self.COLUMN_COUNTRY,
            self.COLUMN_MATH,
            self.COLUMN_FRAME,
            self.COLUMN_KEY
        ])

        self.table.setIconSize(
            QSize(
                self.FLAG_WIDTH,
                self.FLAG_HEIGHT
            )
        )

    def update_bet_info(self, bet):
        """
            Uppdaterar informationen om valt vad.
        """
        self.bet_id_edit.setText(str(bet.id))

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

    def show_key_row_column(
        self,
        visible=True
    ):
        """
            Visar eller döljer kolumnen med U-tecken.
        """
        self.table.setColumnHidden(
            self.COLUMN_KEY,
            not visible
        )

    def update_table(
        self,
        coupon_matches,
        bet_details=None,
        validator=None
    ):
        """
            Uppdaterar detaljtabellen för valt vad.
        """
        self.table.clearContents()
        self.table.setRowCount(len(coupon_matches))

        details = self._build_detail_map(bet_details)

        for row, coupon_match in enumerate(
            coupon_matches
        ):
            detail = details.get(
                row + 1,
                {}
            )

            self._update_detail_row(
                row,
                coupon_match,
                detail,
                validator
            )

        self.table.center_icon_column(self.COLUMN_COUNTRY)

        self.table.set_columns_readonly([
            self.COLUMN_HOME_TEAM,
            self.COLUMN_AWAY_TEAM
        ])

    def _build_detail_map(
        self,
        bet_details
    ):
        """
            Skapar en uppslagstabell med detaljer per match.
        """
        if not bet_details:
            return {}

        return {
            detail.match_number: {
                "frame": detail.frame_value,
                "key": detail.key_value,
                "math": detail.mathematical_value
            }
            for detail in bet_details
        }

    def _update_detail_row(
        self,
        row,
        coupon_match,
        detail,
        validator
    ):
        """
            Uppdaterar en rad i detaljtabellen.
        """
        match = coupon_match.soccer_match

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

        self._set_match_data(
            row,
            match
        )

        math_checkbox = self._create_math_checkbox(
            row,
            saved_frame,
            saved_math
        )

        frame_combo = self._create_frame_combo(
            row,
            saved_frame,
            validator,
            math_checkbox
        )

        key_combo = self._create_key_combo(
            row,
            saved_frame,
            saved_key,
            saved_math,
            validator
        )

        self.table.setCellWidget(
            row,
            self.COLUMN_MATH,
            math_checkbox
        )

        self.table.setCellWidget(
            row,
            self.COLUMN_FRAME,
            frame_combo
        )

        self.table.setCellWidget(
            row,
            self.COLUMN_KEY,
            key_combo
        )

    def _set_match_data(
        self,
        row,
        match
    ):
        """
            Visar matchens land och lag.
        """
        self.table.setCellWidget(
            row,
            self.COLUMN_COUNTRY,
            self._create_flag_widget(match.season.competition)
        )

        self.table.setItem(
            row,
            self.COLUMN_HOME_TEAM,
            QTableWidgetItem(
                match.home_team.display_name
            )
        )

        self.table.setItem(
            row,
            self.COLUMN_AWAY_TEAM,
            QTableWidgetItem(
                match.away_team.display_name
            )
        )

    def _create_math_checkbox(
        self,
        row,
        frame,
        checked
    ):
        """
            Skapar checkboxen för matematisk gardering.
        """
        checkbox = QCheckBox()

        checkbox.setChecked(
            checked
        )

        checkbox.setEnabled(
            frame in self.FRAME_OPTIONS_WITH_KEYS
        )

        checkbox.toggled.connect(
            lambda value, r=row:
            self.math_changed.emit(
                r + 1,
                value
            )
        )

        return checkbox

    def _create_frame_combo(
        self,
        row,
        saved_frame,
        validator,
        math_checkbox
    ):
        """
            Skapar comboboxen för ram.
        """
        frame_values = (
            validator.get_allowed_frame_values(row)
            if validator
            else None
        )

        combo = FrameComboBox(
            frame_values
        )

        index = combo.findText(
            saved_frame
        )

        if index >= 0:
            combo.setCurrentIndex(
                index
            )

        combo.currentTextChanged.connect(
            lambda value,
            r=row,
            checkbox=math_checkbox:
            self._on_frame_changed(
                r,
                value,
                checkbox
            )
        )

        return combo

    def _on_frame_changed(
        self,
        row,
        value,
        checkbox
    ):
        """
            Hanterar ändrad ram.
        """
        self._update_math_checkbox(
            checkbox,
            value
        )

        self.frame_changed.emit(
            row + 1,
            value
        )

    def _create_key_combo(
        self,
        row,
        saved_frame,
        saved_key,
        saved_math,
        validator
    ):
        """
            Skapar comboboxen för U-tecken.
        """
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
                validator.get_allowed_key_values(
                    row
                )
            )
        else:
            key_values = [""]

        combo = KeyComboBox(
            key_values
        )

        index = combo.findText(
            saved_key
        )

        if index >= 0:
            combo.setCurrentIndex(
                index
            )

        combo.setEnabled(
            has_key
            and not saved_math
        )

        combo.currentTextChanged.connect(
            lambda value, r=row:
            self.key_changed.emit(
                r + 1,
                value
            )
        )

        return combo

    def _create_flag_widget(
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

    def refresh_key_combos(
        self,
        validator
    ):
        """
            Uppdaterar alla U-tecken-comboboxar.
        """
        for row in range(
            self.table.rowCount()
        ):
            combo = self.table.cellWidget(
                row,
                self.COLUMN_KEY
            )

            if combo is None:
                continue

            frame_combo = self.table.cellWidget(
                row,
                self.COLUMN_FRAME
            )

            math_checkbox = self.table.cellWidget(
                row,
                self.COLUMN_MATH
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

                self._update_combo_items(
                    combo,
                    values,
                    current
                )

                combo.setEnabled(True)

            else:
                combo.clear()
                combo.addItem("")

                combo.setEnabled(False)

    def _update_math_checkbox(
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

    def _update_combo_items(
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

    def refresh_frame_combos(
        self,
        validator
    ):
        """
            Uppdaterar alla ram-comboboxar.
        """
        for row in range(
            self.table.rowCount()
        ):
            combo = self.table.cellWidget(
                row,
                self.COLUMN_FRAME
            )

            if combo:
                current = combo.currentText()

                values = validator.get_allowed_frame_values(row)

                self._update_combo_items(
                    combo,
                    values,
                    current
                )

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
        self.table.clearSelection()

    def get_bet_result(self):
        """
            Returnerar antal rätt och vinst.
        """
        return (
            self.correct_edit.value(),
            self.prize_edit.value()
        )

    def get_active_selection_table(self):
        return self.table
