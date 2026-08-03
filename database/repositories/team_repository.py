from database.repositories.repository import Repository
from models.domains import Competition, Season, SoccerMatch, Team
import sqlite3


class TeamRepository(Repository):
    """
        Repository för databashantering av fotbollslag.
        Ansvarar för att hämta, skapa, uppdatera och ta bort lag, 
        samt hantera kopplingar mellan lag, säsonger och matcher.
    """

    def __init__(self, database):
        """
            Initierar och skapar en instans av EntityFactory.
        """
        super().__init__(database)

    def get_teams(self, country_id=None):
        """
            Hämtar lag från databasen.
            Om country_id anges, så filtreras resultatet på land.
            Funktionen returnerar en lista med Team-objekt.
        """
        query = """
            SELECT
                t.id                    AS team_id,
                t.country_id            AS team_country_id,
                t.team_name             AS team_name,
                t.display_name          AS team_display_name,
                c.id                    AS team_country_id,
                c.country_name          AS team_country_name,
                c.iso_code              AS team_country_code
            FROM teams t
            JOIN countries c
                ON t.country_id = c.id
        """

        parameters = []

        if country_id is not None:
            query += """
            WHERE c.id = ?
            """
            parameters.append(country_id)

        query += """
            ORDER BY t.team_name
        """

        self.cursor.execute(query, parameters)

        rows = self.cursor.fetchall()

        teams = []

        for row in rows:
            team = self.factory.create_team(row)
            teams.append(team)

        return teams

    def get_available_teams(self, season_id, country_id):
        """
            Hämtar lag som kan läggas till i en säsong.

            Returnerar lag från landet som inte redan
            finns kopplade till säsongen.
        """

        self.cursor.execute(
            """
            SELECT
                t.id                        AS team_id,
                t.team_name                 AS team_name,
                t.display_name              AS team_display_name,
                c.id                        AS team_country_id,
                c.country_name              AS team_country_name,
                c.iso_code                  AS team_country_code
            FROM teams t
            JOIN countries c
                ON c.id=t.country_id
            WHERE t.country_id = ?
            AND t.id NOT IN (
                SELECT st.team_id
                FROM season_teams st
                WHERE st.season_id = ?
            )
            ORDER BY team_name
            """,
            (
                country_id,
                season_id
            )
        )

        rows = self.cursor.fetchall()
        teams = []

        for row in rows:
            team = self.factory.create_team(row)
            teams.append(team)

        return teams

    def add_team(self, country_id, team_name, display_name):
        """
            Lägger till ett nytt lag i databasen.
            Returnerar det skapade lagets id.
        """
        try:
            self.cursor.execute(
                """
                    INSERT INTO teams(
                        country_id,
                        team_name,
                        display_name
                    )
                    VALUES(?, ?, ?)
                """, (
                    country_id,
                    team_name,
                    display_name
                )
            )
            self.connection.commit()
            return self.cursor.lastrowid

        except sqlite3.IntegrityError:
            raise ValueError(
                "Laget finns redan."
            )

    def update_team(
        self,
        team_id,
        country_id,
        team_name,
        display_name
    ):
        """
            Uppdaterar informationen om ett befintligt lag.
        """
        try:
            self.cursor.execute(
                """
                    UPDATE teams
                    SET
                        country_id = ?,
                        team_name = ?,
                        display_name = ?
                    WHERE id = ?
                """, (
                    country_id,
                    team_name,
                    display_name,
                    team_id
                )
            )

            if self.cursor.rowcount == 0:
                raise ValueError(
                    "Laget finns inte."
                )

            self.connection.commit()

        except sqlite3.IntegrityError:
            raise ValueError(
                "Laget finns redan."
            )

    def get_team_id(self, team_name):
        """
            Hämtar id för ett lag baserat på lagnamn.
            Returnerar None om laget inte finns.
        """
        self.cursor.execute(
            """
                SELECT id
                FROM teams
                WHERE team_name = ?
            """,
            (team_name,)
        )
        row = self.cursor.fetchone()

        if row:
            return row["id"]

        return None

    def delete_team(self, team_id):
        """
            Tar bort ett lag från databasen.
            Ett lag kan endast tas bort om det inte
            är kopplat till säsonger eller matcher.
        """
        if self.team_plays_seasons(team_id):
            raise ValueError(
                "Laget kan inte tas bort eftersom det "
                "är kopplat till en eller flera säsonger."
            )

        if self.team_has_matches(team_id):
            raise ValueError(
                "Laget kan inte tas bort eftersom det "
                "finns registrerade matcher."
            )

        self.cursor.execute(
            """
                DELETE FROM teams
                WHERE id = ?
            """, (team_id,)
        )
        self.connection.commit()

    def get_teams_in_season(self, season_id):
        """
            Hämtar alla lag som tillhör en viss säsong.
            Returnerar en lista med Team-objekt.
        """
        self.cursor.execute(
            """
                SELECT
                    t.id                        AS team_id,
                    t.team_name                 AS team_name,        
                    t.display_name              AS team_display_name,
                    c.id                        AS team_country_id,
                    c.country_name              AS team_country_name,
                    c.iso_code                  AS team_country_code
                FROM season_teams st
                JOIN teams t
                    ON st.team_id = t.id
                JOIN countries c
                    ON t.country_id = c.id
                WHERE st.season_id = ?
                ORDER BY t.team_name
            """, (season_id,)
        )
        teams = []
        rows = self.cursor.fetchall()

        for row in rows:
            team = self.factory.create_team(row)
            teams.append(team)

        return teams

    def add_team_to_season(self, season_id, team_id):
        """
            Kopplar ett lag till en säsong.
        """
        self.cursor.execute(
            """
                INSERT OR IGNORE INTO season_teams(
                    season_id,
                    team_id
                )
                VALUES(?, ?)
            """, (
                season_id,
                team_id
            )
        )
        self.connection.commit()

    def team_exists_in_season(self, season_id, team_id):
        """
            Kontrollerar om ett lag är kopplat till en säsong.
            Returnerar True om kopplingen finns.
        """
        self.cursor.execute(
            """
                SELECT 1
                FROM season_teams
                WHERE season_id = ?
                AND team_id = ?
            """, (
                season_id,
                team_id
            )
        )
        return self.cursor.fetchone() is not None

    def team_plays_seasons(self, team_id):
        """
            Kontrollerar om ett lag deltar i någon säsong.
            Returnerar True om laget används i någon säsong.
        """
        self.cursor.execute(
            """
                SELECT 1
                FROM season_teams
                WHERE team_id = ?
                LIMIT 1
            """, (team_id,)
        )
        return self.cursor.fetchone() is not None

    def remove_team_from_season(self, season_id, team_id):
        """
            Tar bort kopplingen mellan ett lag och en säsong.
        """
        if self.team_has_matches_in_season(
            season_id,
            team_id
        ):
            raise ValueError(
                "Laget kan inte tas bort, eftersom det "
                "finns matcher registrerade."
            )

        self.cursor.execute(
            """
                DELETE FROM season_teams
                WHERE season_id = ?
                AND team_id = ?
            """, (season_id, team_id)
        )
        self.connection.commit()

    def get_team_matches(self, season_id, team_id, venue="all"):
        """
            Hämtar matcher för ett lag i en viss säsong.
            venue kan begränsa resultatet till:
            home, away eller all.
            Returnerar en lista med SoccerMatch-objekt.
        """
        query = """
            SELECT
                m.id                    AS soccer_match_id,
                m.match_date            AS soccer_match_date,
                m.home_score            AS soccer_match_home_score,
                m.away_score            AS soccer_match_away_score,
                s.id                    AS soccer_match_season_id,
                s.start_year            AS soccer_match_start_year,
                s.end_year              AS soccer_match_end_year,
                c.id                    AS soccer_match_competition_id,
                c.name                  AS soccer_match_competition_name,
                cc.id                   AS soccer_match_competition_country_id,
                cc.country_name         AS soccer_match_competition_country_name,
                cc.iso_code             AS soccer_match_competition_country_code,
                ht.id AS                soccer_match_home_team_id,
                ht.team_name            AS soccer_match_home_team_name,
                ht.display_name         AS soccer_match_home_team_display_name,
                at.id                   AS soccer_match_away_team_id,
                at.team_name            AS soccer_match_away_team_name,
                at.display_name         AS soccer_match_away_team_display_name
            FROM matches m
            JOIN seasons s
                ON m.season_id = s.id
            JOIN competitions c
                ON s.competition_id = c.id
            JOIN countries cc
                ON c.country_id = cc.id
            JOIN teams ht
                ON m.home_team_id = ht.id
            JOIN teams at
                ON m.away_team_id = at.id
            WHERE m.season_id = ?
        """

        parameters = [season_id]

        if venue == "home":
            query += """
                AND m.home_team_id = ?
            """
            parameters.append(team_id)

        elif venue == "away":
            query += """
                AND m.away_team_id = ?
            """
            parameters.append(team_id)

        else:
            query += """
                AND (
                    m.home_team_id = ?
                    OR
                    m.away_team_id = ?
                )
            """
            parameters.extend(
                [team_id, team_id]
            )

        query += """
            ORDER BY m.match_date DESC
        """

        self.cursor.execute(query, parameters)
        soccer_matches = []
        rows = self.cursor.fetchall()

        for row in rows:
            soccer_match = self.factory.create_soccer_match(row)
            soccer_matches.append(soccer_match)
        return soccer_matches

    def team_has_matches(self, team_id):
        """
            Kontrollerar om ett lag har registrerade matcher.
            Returnerar True om laget förekommer i någon match.
        """
        self.cursor.execute(
            """
                SELECT 1
                FROM matches
                WHERE home_team_id= ?
                OR away_team_id = ?
                LIMIT 1
            """, (
                team_id, team_id
            )
        )
        return self.cursor.fetchone() is not None
