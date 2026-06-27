from PySide6.QtCore import Qt
from mvc import Model, View, Controller
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser

# Klass för att hantera vyn, som visar information om applikationen.


class AboutView(View):
    def __init__(self):
        super().__init__()
        layout = self.create_layout()
        layout.addWidget(
            self.create_header("Om applikationen")
        )
        self.create_about_section(layout)
        self.setLayout(layout)

    # Funktion för att skapa skapa sektionen med information om applikationen.
    def create_about_section(self, layout):
        widget = QWidget()
        widget_layout = QVBoxLayout()

        about = QTextBrowser()
        about.setOpenExternalLinks(True)
        about.setReadOnly(True)

        about.setHtml("""
        <h2>Mitt_Stryktipsprogram</h2>

        <p><b>Version:</b> 1.0</p>

        <p>
        Mitt_Stryktipsprogram är ett program för att skapa, administrera
        och analysera stryktipskuponger.
        Programmet innehåller bland annat funktioner för att:
        </p>

        <ul>
            <li>Skapa och spara kuponger.</li>
            <li>Hantera matcher och resultat.</li>
            <li>Analysera sannolikheter och utdelningar.</li>
            <li>Skriva ut kuponger.</li>          
        </ul>

        <p>
        Programmet är utvecklat i Python med hjälp av PySide6 och SQLite.
        </p>

        <p>
        <b>Utvecklare:</b><br>
        Anders Kleimark
        </p>

        <p>
        © 2026
        </p>
        """)

        widget_layout.addWidget(about)
        widget.setLayout(widget_layout)
        layout.addWidget(widget)
