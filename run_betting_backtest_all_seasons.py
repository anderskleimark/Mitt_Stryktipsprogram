from database.database import Database
from models.analysis.analysis_model import AnalysisModel
from models.backtest.backtest_model import BacktestModel
from models.soccer_model import SoccerModel

COMPETITION_NAME = "Premier League"
SEASONS = ((2021, 2022), (2022, 2023), (2023, 2024), (2024, 2025), (2025, 2026), (2026, 2027))
ODDS_TYPE = "average_closing"
STAKE = 100.0
DETAIL_EV = 0.20


def get_season(database, start_year, end_year):
    database.cursor.execute(
        """
        SELECT seasons.id
        FROM seasons
        JOIN competitions ON competitions.id = seasons.competition_id
        WHERE competitions.competition_name = ?
          AND seasons.start_year = ?
          AND seasons.end_year = ?
        LIMIT 1
        """,
        (COMPETITION_NAME, start_year, end_year)
    )
    row = database.cursor.fetchone()
    if row is None:
        raise ValueError("Säsongen hittades inte.")
    return database.season_repository.get(row["id"])


def team_name(team):
    return (
        getattr(team, "display_name", None)
        or getattr(team, "team_name", None)
        or getattr(team, "name", None)
        or str(team)
    )


def print_table(title, results):
    print("\n" + title)
    print(
        f"{'Min EV':>8} {'Spel':>6} {'Vunna':>7} "
        f"{'Resultat':>11} {'ROI':>9} {'Träff':>9} "
        f"{'Snittodds':>10} {'Modell p':>10} {'Snitt EV':>9}"
    )
    print("-" * 91)
    for r in results:
        print(
            f"{r.minimum_ev:>7.1%} {r.bets:>6} {r.wins:>7} "
            f"{r.profit:>10.0f} {r.roi:>8.2%} {r.hit_rate:>8.2%} "
            f"{r.average_odds:>10.2f} "
            f"{r.average_probability:>9.2%} "
            f"{r.average_expected_value:>8.2%}"
        )


def print_high_ev(predictions):
    bets = sorted(
        (p for p in predictions if p.expected_value >= DETAIL_EV),
        key=lambda p: p.expected_value,
        reverse=True
    )
    print(f"\nEnskilda spel med EV >= {DETAIL_EV:.0%}")
    print(
        f"{'Datum':<12} {'Match':<42} {'Spel':>4} "
        f"{'Modell':>9} {'Odds':>7} {'EV':>9} {'Utfall':>8}"
    )
    print("-" * 99)
    for p in bets:
        match = f"{team_name(p.home_team)} - {team_name(p.away_team)}"
        print(
            f"{str(p.match_date):<12} {match[:42]:<42} "
            f"{p.selection:>4} {p.probability:>8.2%} "
            f"{p.odds:>7.2f} {p.expected_value:>8.2%} "
            f"{('Vinst' if p.won else 'Förlust'):>8}"
        )


def main():
    database = Database()
    try:
        soccer_model = SoccerModel(database)
        analysis_model = AnalysisModel(database, soccer_model)
        backtest_model = BacktestModel(
            soccer_model=soccer_model,
            analysis_model=analysis_model
        )

        all_predictions = []

        for start_year, end_year in SEASONS:
            season = get_season(database, start_year, end_year)
            predictions = backtest_model.betting.run(
                season=season,
                odds_type=ODDS_TYPE
            )
            all_predictions.extend(predictions)

            results = backtest_model.betting.engine.evaluate_all(
                predictions, stake=STAKE
            )
            by_selection = (
                backtest_model.betting.engine.evaluate_by_selection(
                    predictions, stake=STAKE
                )
            )

            print("\n" + "=" * 100)
            print(
                f"{COMPETITION_NAME} "
                f"{start_year}/{str(end_year)[-2:]}"
            )
            print("=" * 100)
            print(f"Oddstyp: {ODDS_TYPE}")
            print(f"Fast insats: {STAKE:.0f} kr")
            print(
                f"Spelkandidater före EV-filter: "
                f"{len(predictions)}"
            )

            print_table("Alla spel", results)
            print_table("Tecken 1", by_selection["1"])
            print_table("Tecken X", by_selection["X"])
            print_table("Tecken 2", by_selection["2"])

        results = backtest_model.betting.engine.evaluate_all(
            all_predictions, stake=STAKE
        )
        by_selection = (
            backtest_model.betting.engine.evaluate_by_selection(
                all_predictions, stake=STAKE
            )
        )

        print("\n" + "=" * 100)
        print("SAMMANLAGT 2021/22–2026/27")
        print("=" * 100)
        print(f"Oddstyp: {ODDS_TYPE}")
        print(f"Fast insats: {STAKE:.0f} kr")
        print(
            f"Spelkandidater före EV-filter: "
            f"{len(all_predictions)}"
        )

        print_table("Alla spel", results)
        print_table("Tecken 1", by_selection["1"])
        print_table("Tecken X", by_selection["X"])
        print_table("Tecken 2", by_selection["2"])

        print_high_ev(all_predictions)

    finally:
        database.close()


if __name__ == "__main__":
    main()
