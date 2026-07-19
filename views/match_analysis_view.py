from mvc import View


class MatchAnalysisView(View):
    def __init__(self):
        super().__init__()

        self.layout = self.create_layout()
        self.create_header("Matchanalys")
        self.layout.addWidget(self.header)

        self.setLayout(self.layout)
