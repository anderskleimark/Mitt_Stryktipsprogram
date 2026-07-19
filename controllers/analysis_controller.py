from mvc import Controller
from views.coupon_analysis_view import CouponAnalysisView
from views.match_analysis_view import MatchAnalysisView


class AnalysisController(Controller):

    def __init__(
        self,
        analysis_model,
        match_view,
        coupon_view
    ):
        super().__init__(analysis_model, match_view)

        self.match_view = match_view
        self.coupon_view = coupon_view

        self.add_connections()

    def add_connections(self):
        pass
