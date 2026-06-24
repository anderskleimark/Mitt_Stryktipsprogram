from mvc import View


class ShowCouponsView(View):

    def __init__(self):
        super().__init__()

        layout = self.create_layout()

        layout.addWidget(
            self.create_header("Kuponger")
        )

        layout.addSpacing(25)
        self.setLayout(layout)
