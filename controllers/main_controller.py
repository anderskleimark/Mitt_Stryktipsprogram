from mvc import Model, View, Controller


class MainController(Controller):
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def show_result_view(self):
        self.view.stack.setCurrentWidget(
            self.view.result_view
        )
