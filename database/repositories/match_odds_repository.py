from database.repositories.repository import Repository


class MatchOddsRepository(Repository):
    """
        Klass som hanterar odds för fotbollsmatcher
        i databasen.
    """

    def save(
        self,
        *,
        match_id,
        bet365_home=None,
        bet365_draw=None,
        bet365_away=None,
        max_home=None,
        max_draw=None,
        max_away=None,
        average_home=None,
        average_draw=None,
        average_away=None,
        bet365_closing_home=None,
        bet365_closing_draw=None,
        bet365_closing_away=None,
        max_closing_home=None,
        max_closing_draw=None,
        max_closing_away=None,
        average_closing_home=None,
        average_closing_draw=None,
        average_closing_away=None,
        source=None
    ):
        """
            Sparar odds för en match.

            Om odds redan finns för matchen
            uppdateras den befintliga posten.
        """
        self.cursor.execute(
            """
                INSERT INTO match_odds (
                    match_id,

                    bet365_home,
                    bet365_draw,
                    bet365_away,

                    max_home,
                    max_draw,
                    max_away,

                    average_home,
                    average_draw,
                    average_away,

                    bet365_closing_home,
                    bet365_closing_draw,
                    bet365_closing_away,

                    max_closing_home,
                    max_closing_draw,
                    max_closing_away,

                    average_closing_home,
                    average_closing_draw,
                    average_closing_away,

                    source
                )
                VALUES (
                    ?, ?, ?, ?,
                    ?, ?, ?,
                    ?, ?, ?,
                    ?, ?, ?,
                    ?, ?, ?,
                    ?, ?, ?,
                    ?
                )
                ON CONFLICT(match_id)
                DO UPDATE SET
                    bet365_home =
                        excluded.bet365_home,
                    bet365_draw =
                        excluded.bet365_draw,
                    bet365_away =
                        excluded.bet365_away,

                    max_home =
                        excluded.max_home,
                    max_draw =
                        excluded.max_draw,
                    max_away =
                        excluded.max_away,

                    average_home =
                        excluded.average_home,
                    average_draw =
                        excluded.average_draw,
                    average_away =
                        excluded.average_away,

                    bet365_closing_home =
                        excluded.bet365_closing_home,
                    bet365_closing_draw =
                        excluded.bet365_closing_draw,
                    bet365_closing_away =
                        excluded.bet365_closing_away,

                    max_closing_home =
                        excluded.max_closing_home,
                    max_closing_draw =
                        excluded.max_closing_draw,
                    max_closing_away =
                        excluded.max_closing_away,

                    average_closing_home =
                        excluded.average_closing_home,
                    average_closing_draw =
                        excluded.average_closing_draw,
                    average_closing_away =
                        excluded.average_closing_away,

                    source =
                        excluded.source
            """,
            (
                match_id,

                bet365_home,
                bet365_draw,
                bet365_away,

                max_home,
                max_draw,
                max_away,

                average_home,
                average_draw,
                average_away,

                bet365_closing_home,
                bet365_closing_draw,
                bet365_closing_away,

                max_closing_home,
                max_closing_draw,
                max_closing_away,

                average_closing_home,
                average_closing_draw,
                average_closing_away,

                source
            )
        )

        self.connection.commit()

    def get_by_match_id(self, match_id):
        """
            Hämtar odds för en match.
        """
        self.cursor.execute(
            self._select_query()
            + """
                WHERE mo.match_id = ?
            """,
            (match_id,)
        )

        row = self.cursor.fetchone()

        if row is None:
            return None

        return self.factory.create_match_odds(row)

    def get_all(self):
        """
            Hämtar samtliga registrerade odds.
        """
        self.cursor.execute(
            self._select_query()
            + """
                ORDER BY m.match_date
            """
        )

        rows = self.cursor.fetchall()

        return [
            self.factory.create_match_odds(row)
            for row in rows
        ]

    @staticmethod
    def _select_query():
        """
            Returnerar den gemensamma SELECT-frågan
            för odds och tillhörande match.
        """
        return """
            SELECT
                mo.id
                    AS match_odds_id,

                mo.bet365_home
                    AS match_odds_bet365_home,
                mo.bet365_draw
                    AS match_odds_bet365_draw,
                mo.bet365_away
                    AS match_odds_bet365_away,

                mo.max_home
                    AS match_odds_max_home,
                mo.max_draw
                    AS match_odds_max_draw,
                mo.max_away
                    AS match_odds_max_away,

                mo.average_home
                    AS match_odds_average_home,
                mo.average_draw
                    AS match_odds_average_draw,
                mo.average_away
                    AS match_odds_average_away,

                mo.bet365_closing_home
                    AS match_odds_bet365_closing_home,
                mo.bet365_closing_draw
                    AS match_odds_bet365_closing_draw,
                mo.bet365_closing_away
                    AS match_odds_bet365_closing_away,

                mo.max_closing_home
                    AS match_odds_max_closing_home,
                mo.max_closing_draw
                    AS match_odds_max_closing_draw,
                mo.max_closing_away
                    AS match_odds_max_closing_away,

                mo.average_closing_home
                    AS match_odds_average_closing_home,
                mo.average_closing_draw
                    AS match_odds_average_closing_draw,
                mo.average_closing_away
                    AS match_odds_average_closing_away,

                mo.source
                    AS match_odds_source,

                m.id
                    AS soccer_match_id,
                m.match_date
                    AS soccer_match_date,
                m.home_score
                    AS soccer_match_home_score,
                m.away_score
                    AS soccer_match_away_score,

                s.id
                    AS soccer_match_season_id,
                s.start_year
                    AS soccer_match_season_start_year,
                s.end_year
                    AS soccer_match_season_end_year,

                c.id
                    AS soccer_match_competition_id,
                c.competition_name
                    AS soccer_match_competition_name,

                cc.id
                    AS soccer_match_competition_country_id,
                cc.country_name
                    AS soccer_match_competition_country_name,
                cc.iso_code
                    AS soccer_match_competition_country_code,

                ht.id
                    AS soccer_match_home_team_id,
                ht.team_name
                    AS soccer_match_home_team_name,
                ht.display_name
                    AS soccer_match_home_team_display_name,

                hc.id
                    AS soccer_match_home_team_country_id,
                hc.country_name
                    AS soccer_match_home_team_country_name,
                hc.iso_code
                    AS soccer_match_home_team_country_code,

                at.id
                    AS soccer_match_away_team_id,
                at.team_name
                    AS soccer_match_away_team_name,
                at.display_name
                    AS soccer_match_away_team_display_name,

                ac.id
                    AS soccer_match_away_team_country_id,
                ac.country_name
                    AS soccer_match_away_team_country_name,
                ac.iso_code
                    AS soccer_match_away_team_country_code

            FROM match_odds mo

            JOIN matches m
                ON m.id = mo.match_id

            JOIN seasons s
                ON s.id = m.season_id

            JOIN competitions c
                ON c.id = s.competition_id

            JOIN countries cc
                ON cc.id = c.country_id

            JOIN teams ht
                ON ht.id = m.home_team_id

            JOIN countries hc
                ON hc.id = ht.country_id

            JOIN teams at
                ON at.id = m.away_team_id

            JOIN countries ac
                ON ac.id = at.country_id
        """