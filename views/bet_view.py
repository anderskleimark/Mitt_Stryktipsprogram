from PySide6.QtCore import Signal
from PySide6.QtWidgets import QStackedWidget, QWidget

from misc.buttons import (AddButton, BackButton, CopyDiagramButton,
                          DeleteButton, OpenGraphButton, SaveAsImageButton,
                          ShowDetailsButton, ShowOverviewButton)
from misc.dialogs.add_bet_dialog import AddBetDialog
from mvc import View
from widgets.bet_detail_widget import BetDetailWidget
from widgets.bet_graph_widget import BetGraphWidget
from widgets.bet_overview_widget import BetOverviewWidget


class BetView(View):
    """
        Vy för att visa och hantera vad.
    """

    # --------------------------------------------------
    # Signaler
    # --------------------------------------------------
    bet_selection_changed = Signal()
    bet_result_changed = Signal()
    frame_changed = Signal(int, str)
    key_changed = Signal(int, str)
    math_changed = Signal(int, bool)

    VIEW_TITLE = "Vad"
    GRAPH_TITLE = "Statistik"

    def __init__(self):
        super().__init__()

        self.layout = self.create_main_layout()
        self.create_header(self.VIEW_TITLE)
        self.layout.addWidget(self.header)

        self.stacked_widget = QStackedWidget()

        self.overview_widget = BetOverviewWidget()
        self.stacked_widget.addWidget(self.overview_widget)

        self.detail_widget = BetDetailWidget()
        self.stacked_widget.addWidget(self.detail_widget)

        self.graph_widget = BetGraphWidget()
        self.stacked_widget.addWidget(self.graph_widget)

        self.layout.addWidget(self.stacked_widget)
        self.create_bottom_widget()
        self.setLayout(self.layout)

        self._setup_signals()

        self.show_overview()

    def _setup_signals(self):
        """
            Vidarebefordrar signaler från subwidgetarna.
        """
        self.overview_widget.bet_selection_changed.connect(
            self.bet_selection_changed.emit)

        self.detail_widget.bet_result_changed.connect(
            self.bet_result_changed.emit
        )

        self.detail_widget.frame_changed.connect(
            self.frame_changed.emit
        )

        self.detail_widget.key_changed.connect(
            self.key_changed.emit
        )

        self.detail_widget.math_changed.connect(
            self.math_changed.emit
        )

    # --------------------------------------------------
    # Bottenpanel
    # --------------------------------------------------

    def create_bottom_widget(self):
        """
            Skapar den nedre knappraden.
        """
        self.bottom_widget = QWidget()

        layout = self.create_horizontal_layout(
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
        current_widget = self.stacked_widget.currentWidget()

        if hasattr(current_widget, "get_active_selection_table"):
            return current_widget.get_active_selection_table()

        return None

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

    # --------------------------------------------------
    # Delegationsmetoder
    # --------------------------------------------------
    def get_selected_bet_row(self):
        """
            Returnerar vald rad i översikten.
        """
        return self.overview_widget.get_selected_row()

    def get_bet_result(self):
        """
            Returnerar antal rätt och vinst.
        """
        return self.detail_widget.get_bet_result()

    def update_bet_info(self, bet):
        """
            Uppdaterar information om valt vad.
        """
        self.detail_widget.update_bet_info(
            bet
        )

    def clear_bet_info(self):
        """
            Rensar information om valt vad.
        """
        self.detail_widget.clear_bet_info()

    def update_detail_table(
        self,
        coupon_matches,
        bet_details=None,
        validator=None
    ):
        """
            Uppdaterar detaljtabellen.
        """
        self.detail_widget.update_table(
            coupon_matches,
            bet_details,
            validator
        )

    def update_system_statistics(
        self,
        statistics
    ):
        """
            Uppdaterar systemstatistiken.
        """
        self.detail_widget.update_system_statistics(statistics)

    def refresh_frame_combos(
        self,
        validator
    ):
        self.detail_widget.refresh_frame_combos(validator)

    def refresh_key_combos(
        self,
        validator
    ):
        self.detail_widget.refresh_key_combos(validator)

    def show_key_row_column(
        self,
        visible=True
    ):
        self.detail_widget.show_key_row_column(visible)

    def update_overview_table(
        self,
        bets
    ):
        self.overview_widget.update_widget(bets)

    def update_bet_result_row(
        self,
        row,
        correct_count,
        prize
    ):
        self.overview_widget.update_bet_result_row(
            row,
            correct_count,
            prize
        )

    def update_statistic_graph(
        self,
        data,
        average
    ):
        self.graph_widget.update_statistic_graph(
            data,
            average
        )

    def copy_diagram_to_clipboard(self):
        self.graph_widget.copy_diagram_to_clipboard()

    def save_diagram_as_image(self):
        self.graph_widget.save_diagram_as_image()
