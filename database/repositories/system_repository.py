import sqlite3

from database.repositories.repository import Repository


class SystemRepository(Repository):
    """
        Klass som hanterar tipssystem i databasen.
    """

    def add_system(
        self,
        *,
        system_type,
        full_covers,
        half_covers,
        row_count
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
                        row_count
                    )
                    VALUES(?, ?, ?, ?)
                """, (
                    system_type,
                    full_covers,
                    half_covers,
                    row_count
                )
            )
            self.connection.commit()
            return self.cursor.lastrowid

        except sqlite3.IntegrityError as exc:
            raise ValueError(
                "Tipssystemet finns redan."
            ) from exc

    def get(self, system_id):
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
                    row_count
                FROM systems
                WHERE id= ?
            """,
            (system_id,)
        )
        row = self.cursor.fetchone()
        if row:
            return self.factory.create_system(row)

        return None

    def get_all_systems(self):
        """
            Hämtar alla tipssystem.
        """
        self.cursor.execute(
            """
                SELECT 
                id              AS system_id, 
                system_type, 
                full_covers, 
                half_covers, 
                row_count
                FROM systems
                ORDER BY full_covers DESC, half_covers DESC, row_count DESC
            """
        )
        rows = self.cursor.fetchall()
        systems = []
        for row in rows:
            system = self.factory.create_system(row)
            systems.append(system)
        return systems

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

    def get_bet_count_for_system(self, system_id):
        """
            Hämtar antal vad kopplade till ett system.
        """
        self.cursor.execute(
            """
                SELECT COUNT(*)
                FROM bets
                WHERE system_id = ?
            """,
            (system_id,)
        )
        return self.cursor.fetchone()[0]
