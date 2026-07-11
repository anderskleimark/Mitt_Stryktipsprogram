from mvc import Model, View, Controller

# Klass (Controller), som agerar vid byte av menyalternativ.


class MainController(Controller):
    def __init__(self, model, view):
        super().__init__(model, view)

    # Funktion för att visa en specifik vy med hjälp av namnet.
    def show_view(self, name):
        self.view.stack.setCurrentWidget(
            self.view.views[name]
        )
