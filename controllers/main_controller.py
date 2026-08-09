from mvc import Controller


class MainController(Controller):
    """
        Controller som hanterar navigering mellan applikationens vyer.

        Klassen ansvarar för att visa rätt vy när användaren väljer ett
        menyalternativ. Innan en vy visas anropas motsvarande controllers
        metod `on_show_view()`, vilket ger controllern möjlighet att
        uppdatera eller förbereda vyn.
    """

    def __init__(self, view):
        """
            Initierar klassen och kopplar vyer till respektive controller.
        """
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
            "setting_view": view.setting_controller,

        }

    def add_connections(self):
        """
            Kopplar samman signaler och slots.
            MainController använder inga egna signaler.
        """

    def show_view(self, name):
        """
            Visar den angivna vyn.

            Om vyn har en tillhörande controller anropas först
            `on_show_view()` så att controllern kan uppdatera vyn innan
            den visas.
            Args:
                name (str): Namnet på den vy som ska visas.
        """
        controller = self.view_controllers.get(name)

        if controller:
            controller.on_show_view()

        self.view.stack.setCurrentWidget(
            self.view.views[name]
        )
