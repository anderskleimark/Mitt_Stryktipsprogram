from mvc import Controller

# Klass (Controller), som agerar vid byte av menyalternativ.


class MainController(Controller):
    def __init__(self, view):
        super().__init__(view)
        self.view_controllers = {
            "team_view": view.team_controller,
            "coupon_view": view.coupon_controller,
            "system_view": view.system_controller,
            "bet_view": view.bet_controller,
            "create_own_system_view": view.create_own_system_controller,
            "competition_view": view.competition_controller,
            "match_analysis_view": view.analysis_controller,
            "coupon_analysis_view": view.analysis_controller,
        }

    def add_connections(self):
        pass

    # Funktion för att visa en specifik vy med hjälp av namnet.
    def show_view(self, name):
        controller = self.view_controllers.get(name)

        if controller:
            controller.activate()

        self.view.stack.setCurrentWidget(
            self.view.views[name]
        )
