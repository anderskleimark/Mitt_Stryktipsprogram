from mvc import View


class CouponAnalysisView(View):
    def __init__(self):
        super().__init__()

        self.layout = self.create_layout()
        self.create_header("Analys av tipskuponger")
        self.layout.addWidget(self.header)

        self.setLayout(self.layout)
