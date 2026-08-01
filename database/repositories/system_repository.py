from database.repositories.repository import Repository


class SystemRepository(Repository):
    """
        Klass som hanterar tipssystem i databasen.
    """

    def __init__(self, database):
        super().__init__(database)

    def add_system(
        self,
        system_type,
        full_covers,
        half_covers,
        rows
    ):
        """
            Lägger till ett nytt tipssystem.
        """
        try:
            self.cursor.execute(
                """
                    INSERT INTO systems(
                        system_type,
                        full_covers,
                        half_covers,
                        rows
                    )
                    VALUES(?, ?, ?, ?)
                """, (
                    system_type,
                    full_covers,
                    half_covers,
                    rows
                )
            )
            self.connection.commit()
            return self.cursor.lastrowid

        except sqlite3.IntegrityError:
            raise ValueError(
                f"Tipssystemet finns redan."
            )

    def get_system_row(self, system_id):
        """
            Hämtar ett tippsystem via id.
        """
        self.cursor.execute(
            """
                SELECT
                    id,
                    system_type,
                    full_covers,
                    half_covers,
                    rows
                FROM systems
                WHERE id= ?
            """,
            (system_id)
        )
        return self.cursor.fetchone()

    def get_all_systems(self):
        """
            Hämtar alla tipssystem.
        """
        self.cursor.execute(
            """
                SELECT id, system_type, full_covers, half_covers, row_count
                FROM systems            
            """
        )
        return self.cursor.fetchall()

    def delete_system(self, system_id):
        """
            Hämtar alla tipssystem.
        """
        # Antal vad som använder detta tipssystem.
        bet_count = self.get_bet_count_for_system(system_id)

        if bet_count > 0:
            raise ValueError(
                f"Systemet används av {bet_count} sparade "
                f"vad och kan därför inte raderas."
            )

        self.cursor.execute(
            """
                DELETE FROM systems
                WHERE id = ?
                """,
            (system_id,)
        )
        self.connection.commit()
