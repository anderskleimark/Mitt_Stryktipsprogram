from mvc import View


class LeagueView(View):

    def __init__(self):
        super().__init__()

        self.layout = self.create_layout()
        self.create_header("Ligor och lag")
        self.layout.addWidget(self.header)

        self.setLayout(self.layout)
