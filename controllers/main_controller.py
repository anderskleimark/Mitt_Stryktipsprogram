from mvc import Model, View, Controller


class MainController(Controller):
    def __init__(self, model, view):
        self.model = model
        self.view = view

    # Funktion för att visa en specifik vy med hjälp av namnet.
    def show_view(self, name):
        self.view.stack.setCurrentWidget(
            self.view.views[name]
        )
