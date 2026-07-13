from mvc import Controller

# Klass (Controller), som agerar vid byte av menyalternativ.


class MainController(Controller):

    def add_connections(self):
        pass

    # Funktion för att visa en specifik vy med hjälp av namnet.
    def show_view(self, name):
        self.view.stack.setCurrentWidget(
            self.view.views[name]
        )
