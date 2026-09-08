from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from PySide6.QtGui import QIcon


@dataclass
class AnalysisData:
    """
        Innehåller all information som behövs
        för att analysera en fotbollsmatch.
    """
    season: Season

    home_team: Team
    away_team: Team

    reference_date: date

    # Aktuell säsong.
    home_matches: list[SoccerMatch]
    away_matches: list[SoccerMatch]
    season_matches: list[SoccerMatch]

    # Alla matcher som används vid
    # Dixon-Coles-passningen.
    model_matches: list[SoccerMatch]

    # Historiska matcher för de två lag
    # som analyseras.
    team_model_matches: dict[
        int,
        list[SoccerMatch]
    ]

    season_statistics: SeasonStatistics

    season_team_statistics: dict[
        int,
        TeamStatistics
    ]

    home_statistics: TeamStatistics
    away_statistics: TeamStatistics

    h2h_statistics: HeadToHeadStatistics


@dataclass
class BacktestPrediction:
    """
        Representerar en historisk prognos
        som används vid backtesting.
    """
    match_date: date

    home_team: Team
    away_team: Team

    probability_1: float
    probability_x: float
    probability_2: float

    actual_result: str


@dataclass
class BacktestResult:
    """
        Innehåller det sammanlagda resultatet
        från ett backtest.
    """
    predictions: list[BacktestPrediction]

    matches_tested: int

    brier_score: float
    log_loss: float
    accuracy: float

    uniform_brier_score: float
    uniform_log_loss: float

    historical_brier_score: float
    historical_log_loss: float

    calibration_bins: list[CalibrationBin]


@dataclass
class Bet:
    """
        Representerar ett spelat stryktips-
        eller oddsspel.
    """
    id: int
    bet_date: str
    correct_count: int | None = None
    prize: int | None = None
    total_cost: int | None = None
    system: System | None = None
    coupon: Coupon | None = None


@dataclass
class BetAnalysis:
    """
        Analys av ett enskilt spelalternativ.
    """
    probability: float
    fair_odds: float
    minimum_odds: float


@dataclass
class BetDetails:
    """
        Innehåller detaljer om ett vad.
    """
    bet: Bet
    match_number: int
    frame_value: str
    key_value: str | None = None
    mathematical_value: bool = False


@dataclass
class CalibrationBin:
    """
        Innehåller resultat för ett intervall
        i modellens kalibreringstest.
    """
    lower_bound: float
    upper_bound: float

    average_probability: float
    actual_frequency: float

    observations: int


@dataclass
class Competition:
    """
        Representerar en fotbollstävling
        eller liga.
    """
    id: int
    competition_name: str
    country: Country

    @property
    def flag_path(self):
        """
            Returnerar sökvägen till
            tävlingens landsflagga.
        """
        return self.country.flag_path

    @property
    def display_name(self):
        """
            Returnerar tävlingens visningsnamn.
        """
        return self.competition_name


@dataclass
class Country:
    """
        Representerar ett land.
    """
    id: int
    country_name: str
    iso_code: str

    FLAG_CODES = {
        "Afghanistan": "af",
        "Albanien": "al",
        "Algeriet": "dz",
        "Andorra": "ad",
        "Angola": "ao",
        "Antigua och Barbuda": "ag",
        "Argentina": "ar",
        "Armenien": "am",
        "Australien": "au",
        "Azerbajdzjan": "az",

        "Belgien": "be",
        "Brasilien": "br",
        "Bulgarien": "bg",

        "Chile": "cl",
        "Colombia": "co",

        "Danmark": "dk",

        "England": "eng",

        "Finland": "fi",
        "Frankrike": "fr",

        "Ghana": "gh",
        "Grekland": "gr",

        "Indien": "in",
        "Irland": "ie",
        "Island": "is",
        "Italien": "it",

        "Japan": "jp",

        "Kanada": "ca",
        "Kina": "cn",
        "Kroatien": "hr",

        "Marocko": "ma",
        "Mexiko": "mx",

        "Nederländerna": "nl",
        "Norge": "no",
        "Nya Zeeland": "nz",

        "Polen": "pl",
        "Portugal": "pt",

        "Rumänien": "ro",
        "Ryssland": "ru",

        "Schweiz": "ch",
        "Serbien": "rs",
        "Skottland": "sct",
        "Spanien": "es",
        "Sverige": "se",
        "Sydafrika": "za",
        "Sydkorea": "kr",

        "Tjeckien": "cz",
        "Turkiet": "tr",
        "Tyskland": "de",

        "Ukraina": "ua",
        "Uruguay": "uy",
        "USA": "us",

        "Wales": "wls",

        "Österrike": "at",
    }

    @classmethod
    def get_flag_path(cls, country):
        """
            Returnerar sökvägen till landets flagga.
            Om landet saknas returneras unknown.png.
        """
        code = cls.FLAG_CODES.get(country)

        if code is None:
            return str(
                Path("resources")
                / "flags"
                / "unknown.png"
            )

        return str(
            Path("resources")
            / "flags"
            / f"{code}.svg"
        )

    @property
    def flag_path(self):
        """
            Returnerar sökvägen till
            landets flagga.
        """
        return self.get_flag_path(self.country_name)

    @property
    def flag_icon(self):
        """
            Returnerar landets flagga
            som en QIcon.
        """
        return QIcon(self.flag_path)

    @property
    def display_name(self):
        """
            Returnerar landets visningsnamn.
        """
        return self.country_name


@dataclass
class CouponMatch:
    """
        Kopplar ett matchnummer på kupongen
        till en fotbollsmatch.
    """
    match_number: int
    soccer_match: SoccerMatch


@dataclass
class Coupon:
    """
        Representerar en stryktipskupong.
    """
    id: int
    coupon_year: int
    coupon_week: int
    soccer_matches: list[CouponMatch] = field(
        default_factory=list
    )


@dataclass
class DixonColesParameters:
    """
        Innehåller parametrarna från en
        gemensamt skattad Dixon-Coles-modell.
    """

    # Logaritmisk attackstyrka per lag.
    attack: dict[int, float]

    # Logaritmisk försvarsstyrka per lag.
    # Högre värde innebär bättre försvar.
    defence: dict[int, float]

    # Effekt per tävling.
    # Referenstävlingen har alltid 0.0.
    competition_effect: dict[int, float]

    # Gemensam grundnivå för mål.
    base_log_rate: float

    # Hemmafördel på log-skalan.
    home_advantage: float

    # Dixon-Coles beroendeparameter.
    rho: float

    # Tävlingen som används som referens.
    reference_competition_id: int

    # Information om optimeringen.
    success: bool
    negative_log_likelihood: float
    matches_used: int


@dataclass
class FormBacktestResult:
    """
        Resultat från ett backtest för en
        kombination av antal formmatcher
        och formvikt.
    """
    form_match_count: int
    form_weight: float

    matches_tested: int

    brier_score: float
    log_loss: float
    accuracy: float

    uniform_brier_score: float
    uniform_log_loss: float

    historical_brier_score: float
    historical_log_loss: float

    calibration_bins: list[CalibrationBin]


@dataclass
class FormExpectation:
    """
        Förväntat resultat för hemma- och bortalag inför en historisk match.
    """
    home_expected_result: float
    away_expected_result: float


@dataclass
class HeadToHeadStatistics:
    """
        Innehåller statistik om inbördes möten.
    """
    matches: int
    home_wins: int
    home_draws: int
    home_losses: int
    home_score: str

    away_wins: int
    away_draws: int
    away_losses: int
    away_score: str


@dataclass
class HistoryYearsBacktestResult:
    """
        Resultat från ett backtest
        för en viss historiklängd.
    """
    history_years: int

    matches_tested: int

    brier_score: float
    log_loss: float
    accuracy: float

    uniform_brier_score: float
    uniform_log_loss: float

    historical_brier_score: float
    historical_log_loss: float

    calibration_bins: list[CalibrationBin]


@dataclass
class MatchAnalysis:
    """
        Innehåller resultatet av en analys
        av en fotbollsmatch.
    """

    home_statistics: TeamStatistics
    away_statistics: TeamStatistics
    h2h_statistics: HeadToHeadStatistics

    lambda_home: float
    lambda_away: float

    # Poissonfördelning för respektive lags mål.
    home_poisson: list[float]
    away_poisson: list[float]

    # Dixon-Coles-parameter.
    rho: float

    most_likely_scores: list[
        tuple[int, int, float]
    ]

    score_matrix: list[
        list[float]
    ]

    odds_analysis: OddsAnalysis


@dataclass
class OddsAnalysis:
    """
        Oddsanalys för matchens olika
        spelmarknader.
    """
    match_result: dict[str, BetAnalysis]
    double_chance: dict[str, BetAnalysis]
    over_under: dict[float, dict[str, BetAnalysis]]
    btts: dict[str, BetAnalysis]


@dataclass
class OddsData:
    """
        Bookmakerodds för matchens
        spelmarknader.
    """
    match_result: dict[str, float]
    double_chance: dict[str, float]
    over_under: dict[float, dict[str, float]]
    btts: dict[str, float]


@dataclass
class Setting:
    """
        Hanterar olika inställningar.
    """
    data: dict[str, str] = field(
        default_factory=dict
    )


@dataclass
class Season:
    """
        Representerar en säsong
        för en fotbollstävling.
    """
    id: int
    competition: Competition
    start_year: int
    end_year: int

    @property
    def name(self):
        """
            Returnerar säsongens namn.
        """
        if self.start_year == self.end_year:
            return str(self.start_year)

        return (
            f"{self.start_year} / "
            f"{self.end_year}"
        )

    @property
    def display_name(self):
        """
            Returnerar säsongens visningsnamn.
        """
        return (
            f"{self.competition.competition_name} "
            f"{self.name}"
        )


@dataclass
class SeasonStatistics:
    """
        Innehåller sammanfattande statistik
        för en hel säsong.
    """
    matches_played: int = 0
    total_home_goals: int = 0
    total_away_goals: int = 0

    @property
    def average_home_goals(self):
        """
            Returnerar genomsnittligt antal
            hemmamål per match.
        """
        if self.matches_played == 0:
            return 0.0

        return (
            self.total_home_goals
            / self.matches_played
        )

    @property
    def average_away_goals(self):
        """
            Returnerar genomsnittligt antal
            bortamål per match.
        """
        if self.matches_played == 0:
            return 0.0

        return (
            self.total_away_goals
            / self.matches_played
        )

    @property
    def home_advantage(self):
        """
            Returnerar kvoten mellan
            hemma- och bortamål.
        """
        if self.average_away_goals == 0:
            return 1.0

        return (
            self.average_home_goals
            / self.average_away_goals
        )


@dataclass
class SoccerMatch:
    """
        Representerar en spelad eller
        kommande fotbollsmatch.
    """
    id: int
    season: Season
    home_team: Team
    away_team: Team
    match_date: date | None = None
    home_score: int | None = None
    away_score: int | None = None

    @property
    def result_1x2(self):
        """
            Returnerar matchresultatet
            som 1, X eller 2.
        """
        if (
            self.home_score is None
            or self.away_score is None
        ):
            return ""

        if self.home_score > self.away_score:
            return "1"

        if self.home_score < self.away_score:
            return "2"

        return "X"


@dataclass
class Standing:
    """
        Representerar ett lags tabellplacering
        och statistik i en liga.
    """
    team: Team
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    points: int


@dataclass
class System:
    """
        Representerar ett matematiskt
        eller reducerat tipssystem.
    """
    id: int
    system_type: str
    full_covers: int
    half_covers: int
    row_count: int

    @property
    def type_name(self):
        """
            Returnerar systemtypens namn.
        """
        return {
            "M": "M-system",
            "R": "R-system",
            "U": "U-system"
        }.get(
            self.system_type,
            self.system_type
        )

    @property
    def display_name(self):
        """
            Returnerar systemets visningsnamn.
        """
        return (
            f"{self.system_type} "
            f"{self.full_covers}-"
            f"{self.half_covers}-"
            f"{self.row_count}"
        )


@dataclass
class Team:
    """
        Representerar ett fotbollslag.
    """
    id: int
    country: Country
    team_name: str
    display_name: str


@dataclass
class TeamStatistics:
    """
        Innehåller statistik och modellparametrar
        för ett lag under en säsong.
    """

    team: Team
    season: Season
    matches_played: int = 0

    wins: int = 0
    draws: int = 0
    losses: int = 0

    home_wins: int = 0
    home_draws: int = 0
    home_losses: int = 0

    away_wins: int = 0
    away_draws: int = 0
    away_losses: int = 0

    goals_for: int = 0
    goals_against: int = 0

    home_matches_played: int = 0
    away_matches_played: int = 0

    home_goals_for: int = 0
    home_goals_against: int = 0

    away_goals_for: int = 0
    away_goals_against: int = 0

    home_attack_coefficient: float = 0.0
    home_defence_coefficient: float = 0.0
    away_attack_coefficient: float = 0.0
    away_defence_coefficient: float = 0.0

    recent_form: float = 0.5

    @property
    def goal_difference(self):
        """
            Returnerar lagets målskillnad.
        """
        return self.goals_for - self.goals_against

    @property
    def home_goal_difference(self):
        """
            Returnerar lagets målskillnad
            på hemmaplan.
        """
        return (
            self.home_goals_for
            - self.home_goals_against
        )

    @property
    def away_goal_difference(self):
        """
            Returnerar lagets målskillnad
            på bortaplan.
        """
        return (
            self.away_goals_for
            - self.away_goals_against
        )

    @property
    def goals_for_against(self):
        """
            Returnerar mål för och emot
            som text.
        """
        return (
            f"{self.goals_for} – "
            f"{self.goals_against}"
        )

    @property
    def home_goals_for_against(self):
        """
            Returnerar hemmamål för och
            emot som text.
        """
        return (
            f"{self.home_goals_for} – "
            f"{self.home_goals_against}"
        )

    @property
    def away_goals_for_against(self):
        """
            Returnerar bortamål för och
            emot som text.
        """
        return (
            f"{self.away_goals_for} – "
            f"{self.away_goals_against}"
        )

    @property
    def average_goals_for(self):
        """
            Returnerar genomsnittligt antal
            gjorda mål per match.
        """
        if self.matches_played == 0:
            return 0.0

        return (
            self.goals_for
            / self.matches_played
        )

    @property
    def average_goals_against(self):
        """
            Returnerar genomsnittligt antal
            insläppta mål per match.
        """
        if self.matches_played == 0:
            return 0.0

        return (
            self.goals_against
            / self.matches_played
        )

    @property
    def average_home_goals_for(self):
        """
            Returnerar genomsnittligt antal
            gjorda hemmamål.
        """
        if self.home_matches_played == 0:
            return 0.0

        return (
            self.home_goals_for
            / self.home_matches_played
        )

    @property
    def average_home_goals_against(self):
        """
            Returnerar genomsnittligt antal
            insläppta hemmamål.
        """
        if self.home_matches_played == 0:
            return 0.0

        return (
            self.home_goals_against
            / self.home_matches_played
        )

    @property
    def average_away_goals_for(self):
        """
            Returnerar genomsnittligt antal
            gjorda bortamål.
        """
        if self.away_matches_played == 0:
            return 0.0

        return (
            self.away_goals_for
            / self.away_matches_played
        )

    @property
    def average_away_goals_against(self):
        """
            Returnerar genomsnittligt antal
            insläppta bortamål.
        """
        if self.away_matches_played == 0:
            return 0.0

        return (
            self.away_goals_against
            / self.away_matches_played
        )


@dataclass
class TimeDecayBacktestResult:
    """
        Resultat för ett enskilt
        time-decay-värde.
    """
    time_decay: float

    matches_tested: int

    brier_score: float
    log_loss: float
    accuracy: float

    uniform_brier_score: float
    uniform_log_loss: float

    historical_brier_score: float
    historical_log_loss: float

    calibration_bins: list[CalibrationBin]


@dataclass
class TrainingScopeBacktestResult:
    """
        Resultat från ett backtest för en
        viss omfattning av träningsdata.
    """
    training_scope: str

    matches_tested: int

    brier_score: float
    log_loss: float
    accuracy: float

    uniform_brier_score: float
    uniform_log_loss: float

    historical_brier_score: float
    historical_log_loss: float

    calibration_bins: list[CalibrationBin]
