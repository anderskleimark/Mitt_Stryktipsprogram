from models.domains import MatchAnalysis


class AnalysisEngine:

    def analyze_match(self, data):

        return MatchAnalysis(
            home_statistics=data.home_statistics,
            away_statistics=data.away_statistics,

            lambda_home=0.0,
            lambda_away=0.0,

            probability_1=0.0,
            probability_x=0.0,
            probability_2=0.0,

            probability_over_25=0.0,
            probability_under_25=0.0,

            probability_btts=0.0,

            score_matrix=[]
        )
