from mvc import View
from widgets.year_week_widget import YearWeekWidget


class ShowCouponsView(View):

    def __init__(self):
        super().__init__()

        layout = self.create_layout()

        layout.addWidget(
            self.create_header("Kuponger")
        )

        layout.addSpacing(25)
        self.year_week_widget = YearWeekWidget()
        layout.addWidget(self.year_week_widget)

        self.setLayout(layout)
