import csv
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MatchImportResult:
    """
        Resultat från import av en CSV-fil.
    """
    row_count: int = 0
    imported_matches: int = 0
    updated_matches: int = 0
    imported_odds: int = 0
    skipped_rows: int = 0


class MatchCsvImporter:
    """
        Importerar matcher och odds från
        Football-Data CSV-filer.
    """

    DATE_FORMATS = (
        "%d/%m/%Y",
        "%d/%m/%y"
    )

    def __init__(
        self,
        *,
        database,
        competition_id
    ):
        self.database = database
        self.competition_id = competition_id

        self.season_repository = (
            database.season_repository
        )

        self.team_repository = (
            database.team_repository
        )

        self.match_repository = (
            database.soccer_match_repository
        )

        self.odds_repository = (
            database.match_odds_repository
        )

    def import_file(
        self,
        file_path
    ):
        """
            Importerar matcher från en CSV-fil.
        """
        result = MatchImportResult()

        with open(
            file_path,
            newline="",
            encoding="utf-8-sig"
        ) as file:
            reader = csv.DictReader(file)

            self._validate_columns(
                reader.fieldnames
            )

            for row in reader:
                result.row_count += 1

                try:
                    self._import_row(
                        row,
                        result
                    )
                except ValueError:
                    result.skipped_rows += 1

        return result

    def _import_row(
        self,
        row,
        result
    ):
        """
            Importerar en enskild CSV-rad.
        """
        match_date = self._parse_date(
            row["Date"]
        )

        season = self._find_season(
            match_date
        )

        if season is None:
            raise ValueError(
                "Ingen säsong hittades."
            )

        teams = (
            self.team_repository
            .get_teams_in_season(
                season.id
            )
        )

        home_team = self._find_team(
            row["HomeTeam"],
            teams
        )

        away_team = self._find_team(
            row["AwayTeam"],
            teams
        )

        if home_team is None:
            raise ValueError(
                f"Hemmalaget '{row['HomeTeam']}' "
                "kunde inte identifieras."
            )

        if away_team is None:
            raise ValueError(
                f"Bortalaget '{row['AwayTeam']}' "
                "kunde inte identifieras."
            )

        home_score = self._parse_int(
            row.get("FTHG")
        )

        away_score = self._parse_int(
            row.get("FTAG")
        )

        match_id = (
            self.match_repository.get_match_id(
                season_id=season.id,
                home_team_id=home_team.id,
                away_team_id=away_team.id,
                match_date=match_date
            )
        )

        if match_id is None:
            match_id = (
                self.match_repository.add_match(
                    season_id=season.id,
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    match_date=match_date.isoformat(),
                    home_score=home_score,
                    away_score=away_score
                )
            )

            result.imported_matches += 1

        else:
            self.match_repository.update_match(
                match_id=match_id,
                home_team_id=home_team.id,
                away_team_id=away_team.id,
                match_date=match_date.isoformat(),
                home_score=home_score,
                away_score=away_score
            )

            result.updated_matches += 1

        self._save_odds(
            match_id,
            row
        )

        result.imported_odds += 1

    def _find_season(
        self,
        match_date
    ):
        """
            Hittar den säsong som matchdatumet
            tillhör.
        """
        seasons = (
            self.season_repository.get_seasons(
                self.competition_id
            )
        )

        for season in seasons:
            if (
                match_date.year == season.start_year
                and match_date.month >= 6
            ):
                return season

            if (
                match_date.year == season.end_year
                and match_date.month < 6
            ):
                return season

        return None

    @staticmethod
    def _find_team(
        csv_name,
        teams
    ):
        """
            Matchar ett lagnamn från CSV-filen
            mot ett lag i databasen.
        """
        csv_name = csv_name.strip().casefold()

        exact_matches = [
            team
            for team in teams
            if (
                team.team_name.strip().casefold()
                == csv_name
                or
                team.display_name.strip().casefold()
                == csv_name
            )
        ]

        if len(exact_matches) == 1:
            return exact_matches[0]

        return None

    def _save_odds(
        self,
        match_id,
        row
    ):
        """
            Sparar tillgängliga 1X2-odds.
        """
        self.odds_repository.save(
            match_id=match_id,

            bet365_home=self._parse_float(
                row.get("B365H")
            ),
            bet365_draw=self._parse_float(
                row.get("B365D")
            ),
            bet365_away=self._parse_float(
                row.get("B365A")
            ),

            max_home=self._parse_float(
                row.get("MaxH")
            ),
            max_draw=self._parse_float(
                row.get("MaxD")
            ),
            max_away=self._parse_float(
                row.get("MaxA")
            ),

            average_home=self._parse_float(
                row.get("AvgH")
            ),
            average_draw=self._parse_float(
                row.get("AvgD")
            ),
            average_away=self._parse_float(
                row.get("AvgA")
            ),

            bet365_closing_home=self._parse_float(
                row.get("B365CH")
            ),
            bet365_closing_draw=self._parse_float(
                row.get("B365CD")
            ),
            bet365_closing_away=self._parse_float(
                row.get("B365CA")
            ),

            max_closing_home=self._parse_float(
                row.get("MaxCH")
            ),
            max_closing_draw=self._parse_float(
                row.get("MaxCD")
            ),
            max_closing_away=self._parse_float(
                row.get("MaxCA")
            ),

            average_closing_home=self._parse_float(
                row.get("AvgCH")
            ),
            average_closing_draw=self._parse_float(
                row.get("AvgCD")
            ),
            average_closing_away=self._parse_float(
                row.get("AvgCA")
            ),

            source="Football-Data"
        )

    @classmethod
    def _parse_date(
        cls,
        value
    ):
        value = value.strip()

        for date_format in cls.DATE_FORMATS:
            try:
                return datetime.strptime(
                    value,
                    date_format
                ).date()

            except ValueError:
                continue

        raise ValueError(
            f"Ogiltigt matchdatum: {value}"
        )

    @staticmethod
    def _parse_int(
        value
    ):
        if value is None:
            return None

        value = value.strip()

        if not value:
            return None

        return int(value)

    @staticmethod
    def _parse_float(
        value
    ):
        if value is None:
            return None

        value = value.strip()

        if not value:
            return None

        return float(value)

    @staticmethod
    def _validate_columns(
        fieldnames
    ):
        required = {
            "Date",
            "HomeTeam",
            "AwayTeam",
            "FTHG",
            "FTAG"
        }

        if fieldnames is None:
            raise ValueError(
                "CSV-filen saknar kolumnrubriker."
            )

        missing = (
            required
            - set(fieldnames)
        )

        if missing:
            columns = ", ".join(
                sorted(missing)
            )

            raise ValueError(
                "CSV-filen saknar obligatoriska "
                f"kolumner: {columns}"
            )