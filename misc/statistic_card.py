from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QFrame, QGraphicsDropShadowEffect, QLabel,
                               QProgressBar, QVBoxLayout)


class StatisticCard(QFrame):

    def __init__(self, title):
        super().__init__()

        self.setObjectName("StatisticCard")

        self.setMinimumHeight(70)
        self.setMaximumHeight(75)
        self.setMinimumWidth(140)

        self.setStyleSheet("""
            QFrame#StatisticCard {
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 8px;
            }
        """)

        #
        # Diskret skugga
        #

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setOffset(0, 2)
        shadow.setColor("#33000000")

        self.setGraphicsEffect(shadow)

        #
        # Layout
        #

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            10, 5, 10, 5
        )

        layout.setSpacing(2)

        #
        # Titel
        #

        self.title_label = QLabel(title)

        self.title_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        font = self.title_label.font()
        font.setPointSize(9)

        self.title_label.setFont(font)

        self.title_label.setStyleSheet("""
            color: palette(text);
        """)

        #
        # Huvudvärde
        #

        self.value_label = QLabel("0 / 0")

        self.value_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        font = self.value_label.font()
        font.setPointSize(16)
        font.setBold(True)

        self.value_label.setFont(font)

        #
        # Kvar
        #

        self.remaining_label = QLabel("0 kvar")

        self.remaining_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        font = self.remaining_label.font()
        font.setPointSize(8)

        self.remaining_label.setFont(font)

        self.remaining_label.setStyleSheet("""
            color: palette(mid);
        """)

        #
        # Progressbar
        #

        self.progress = QProgressBar()

        self.progress.setRange(
            0, 100
        )

        self.progress.setValue(
            0
        )

        self.progress.setTextVisible(
            False
        )

        self.progress.setFixedHeight(
            4
        )

        #
        # Lägg till widgets
        #

        layout.addWidget(
            self.title_label
        )

        layout.addWidget(
            self.value_label
        )

        layout.addWidget(
            self.remaining_label
        )

        layout.addSpacing(3)

        layout.addWidget(
            self.progress
        )

        self.update_progress_color(
            "#888888"
        )

    def update_progress_color(self, color):

        self.progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: palette(midlight);
                border-radius: 2px;
                border: none;
            }}

            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 2px;
            }}
        """)

    def update_values(self, used, total):

        remaining = max(
            total - used,
            0
        )

        self.value_label.setText(
            f"{used} / {total}"
        )

        self.remaining_label.setText(
            f"{remaining} kvar"
        )

        if total == 0:

            percent = 0
            left = 0

        else:

            percent = int(
                used / total * 100
            )

            left = remaining / total

        self.progress.setValue(
            percent
        )

        #
        # Gråskala som fungerar i båda teman
        #

        if left > 0.5:

            color = "#AAAAAA"

        elif left > 0.2:

            color = "#777777"

        else:

            color = "#444444"

        self.update_progress_color(
            color
        )
