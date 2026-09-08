from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QAbstractItemView, QHeaderView, QSpinBox,
                               QStyledItemDelegate, QTableWidget)


class CenterIconDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        option.displayAlignment = Qt.AlignCenter
        super().paint(painter, option, index)


class ScoreDelegate(QStyledItemDelegate):
    MIN_VALUE = 0
    MAX_VALUE = 20

    def createEditor(self, parent, _option, _index):
        editor = QSpinBox(parent)
        editor.setRange(self.MIN_VALUE, self.MAX_VALUE)
        return editor

    def setEditorData(self, editor, index):
        text = index.data()

        if text == "":
            editor.setValue(0)
        else:
            editor.setValue(int(text))

    def setModelData(self, editor, model, index):
        model.setData(index, str(editor.value()))


class BaseTableWidget(QTableWidget):
    def __init__(
        self,
        parent=None,
        *,
        readonly=False,
        selection="row",
        row_count=0,
        headers
    ):
        super().__init__(row_count, len(headers), parent)

        self.set_table_readonly(readonly)
        self.set_selection_setting(selection)
        self.setAlternatingRowColors(True)
        self.setHorizontalHeaderLabels(headers)
        self._add_style()

    def _add_style(self):
        self.setStyleSheet("""
            QTableWidget {
                background-color: #151718;
                border: 1px solid #404448;
                border-radius: 8px;
                gridline-color: #292c2f;
            }

            QTableWidget::item {
                border: none;
                padding: 4px;
            }

            QHeaderView::section {
                background-color: #292c2f;
                border: none;
                border-right: 1px solid #404448;
                border-bottom: 1px solid #404448;
                padding: 8px;
            }

            QHeaderView::section:first {
                border-top-left-radius: 7px;
            }

            QHeaderView::section:last {
                border-top-right-radius: 7px;
                border-right: none;
            }
        """)

    def set_selection_setting(self, selection):
        if selection is False:
            self.setSelectionMode(
                QAbstractItemView.SelectionMode.NoSelection
            )

        elif selection == "row":
            self.setSelectionMode(
                QAbstractItemView.SelectionMode.SingleSelection
            )
            self.setSelectionBehavior(
                self.SelectionBehavior.SelectRows
            )

        elif selection == "item":
            self.setSelectionMode(
                QAbstractItemView.SelectionMode.SingleSelection
            )
            self.setSelectionBehavior(
                self.SelectionBehavior.SelectItems
            )

    def clear_current_selection(self):
        self.clearSelection()
        self.setCurrentCell(-1, -1)

    def set_minimum_column_width(self, width):
        if width <= 0:
            return
        header = self.horizontalHeader()
        header.setMinimumSectionSize(width)

    def set_columns_readonly(self, columns):
        for row in range(self.rowCount()):
            for col in columns:
                item = self.item(row, col)
                if item is None:
                    continue
                item.setFlags(
                    item.flags() & ~Qt.ItemFlag.ItemIsEditable
                )

    def has_selected_row(self):
        return self.selectionModel().hasSelection()

    def get_selected_row(self):
        """
            Returnerar index för den markerade raden.

            Returnerar -1 om ingen rad
            är markerad.
        """
        selected_rows = self.selectionModel().selectedRows()

        if not selected_rows:
            return -1

        return selected_rows[0].row()

    def set_wide_column(self, column):
        if column < 0 or column >= self.columnCount():
            return

        header = self.horizontalHeader()
        header.setSectionResizeMode(column, QHeaderView.ResizeMode.Stretch)

    def set_wide_columns(self, columns="all"):
        if columns == "all":
            columns = range(self.columnCount())

        for column in columns:
            self.set_wide_column(column)

    def set_narrow_column(self, column):
        if column < 0 or column >= self.columnCount():
            return

        header = self.horizontalHeader()
        header.setSectionResizeMode(
            column, QHeaderView.ResizeMode.ResizeToContents)

    def set_narrow_columns(self, columns):
        for column in columns:
            self.set_narrow_column(column)

    def center_column(self, column):
        for row in range(self.rowCount()):
            item = self.item(row, column)
            if item:
                item.setTextAlignment(Qt.AlignCenter)

    def center_icon_column(self, column):
        self.setItemDelegateForColumn(
            column,
            CenterIconDelegate(self)
        )

    def set_table_readonly(self, readonly=True):
        if readonly:
            self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        else:
            self.setEditTriggers(QTableWidget.EditTrigger.AllEditTriggers)

    def set_column_numeric(self, column):
        if column < 0 or column >= self.columnCount():
            return
        delegate = ScoreDelegate()
        self.setItemDelegateForColumn(column, delegate)

    def set_columns_numeric(self, columns):
        for column in columns:
            self.set_column_numeric(column)

    def hide_columns(self, columns):
        for column in columns:
            if column < 0 or column >= self.columnCount():
                return
            self.setColumnHidden(column, True)

    def show_columns(self, columns):
        for column in columns:
            if column < 0 or column >= self.columnCount():
                return
            self.setColumnHidden(column, False)

    def set_no_selection(self):
        self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
