from PySide6.QtWidgets import QTableWidget
from PySide6.QtWidgets import QHeaderView
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QStyledItemDelegate, QSpinBox
# Klass för att hantera numeriska kolumner.


class ScoreDelegate(QStyledItemDelegate):
    MIN_VALUE = 0
    MAX_VALUE = 20

    def createEditor(self, parent, option, index):
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

# Klass som ärver QTableWidget.


class BaseTableWidget(QTableWidget):

    def __init__(self, readonly=False, rowselection=True, rows=0, cols=0, parent=None):
        super().__init__(rows, cols, parent)

        self.set_table_readonly(readonly)
        self.set_row_selection_setting(rowselection)
        self.setSelectionMode(self.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(True)

    # Funktion som används för att ställa in om en hel rad eller enstaka celler skall markeras.
    def set_row_selection_setting(self, select=True):
        if select:
            self.setSelectionBehavior(self.SelectionBehavior.SelectRows)
        else:
            self.setSelectionBehavior(self.SelectionBehavior.SelectItems)

    # Funktion för att rensa markeringen.
    def clear_current_selection(self):
        self.clearSelection()
        self.setCurrentCell(-1, -1)

    # Funktion som används för att ställa in den minsta bredden på alla kolumner i tabellen.
    def set_minimum_column_width(self, width):
        if (width <= 0):
            return
        header = self.horizontalHeader()
        header.setMinimumSectionSize(width)

    # Funktion som gör angivna kolumner ej redigeringsbara.
    def set_columns_readonly(self, columns):

        for row in range(self.rowCount()):
            for col in columns:

                item = self.item(row, col)
                if item is None:
                    continue

                item.setFlags(
                    item.flags() & ~Qt.ItemFlag.ItemIsEditable
                )

    # Funktion som returnerar True, om det finns någon rad som är markerad.
    # Om ingen rad är markerad, så returneras False.

    def has_selected_row(self):
        return self.selectionModel().hasSelection()

    # Funktion som returnerar radnumret på den rad som är markerad. Om ingen rad är markerad, så returneras -1.
    def get_selected_row(self):
        if not self.has_selected_row():
            return -1

        return self.currentRow()

    # Ställ in så att en angiven kolumn är bred.
    def set_wide_column(self, column):

        if not 0 <= column < self.columnCount() - 1:
            return

        header = self.horizontalHeader()
        header.setSectionResizeMode(column, QHeaderView.ResizeMode.Stretch)

    # Funktion för att sätta vilka kolumner som skall vara breda.
    def set_wide_columns(self, columns):
        for column in columns:
            self.set_wide_column(column)

    # Ställ in så att en angiven kolumn är smal.
    def set_narrow_column(self, column):
        if not 0 <= column <= self.columnCount() - 1:
            return
        header = self.horizontalHeader()
        header.setSectionResizeMode(
            column, QHeaderView.ResizeMode.ResizeToContents)

    # Funktion för att sätta vilka kolumner som skall vara så smala som möjligt.
    def set_narrow_columns(self, columns):
        for column in columns:
            self.set_narrow_column(column)

    # Funktion som ställer in så att hela tabellen är ej redigerbar (om readonly=True) eller tvärtom (om readonly=False).
    def set_table_readonly(self, readonly=True):
        if readonly:
            self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        else:
            self.setEditTriggers(QTableWidget.EditTrigger.AllEditTriggers)

    # Funktion som gör en angiven kolumn numerisk.
    def set_column_numeric(self, column):
        if not 0 <= column <= self.columnCount() - 1:
            return
        delegate = ScoreDelegate()
        self.setItemDelegateForColumn(column, delegate)

    # Funktion som gör kolumner numeriska.
    def set_columns_numeric(self, columns):
        for column in columns:
            self.set_column_numeric(column)
