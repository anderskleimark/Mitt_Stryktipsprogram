from database.repositories.repository import Repository


class SystemRepository(Repository):
    def __init__(self, database):
        super().__init__(database)

    # Funktion som skapar ett nytt tipssystem i databasen med hjälp
    # av typ av system, antalet helgarderingar, antalet halvgarderingar och antalet rader.
    # Funktionen returnerar det id som tipssystemet får.
    def create_system(
        self,
        system_type,
        full_covers,
        half_covers,
        rows
    ):

        try:
            self.cursor.execute("""
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
            ))

            self.connection.commit()
            return self.cursor.lastrowid

        except sqlite3.IntegrityError:
            raise ValueError(
                f"Tipssystemet finns redan."
            )

    # Funktion som hämtar information om ett tipssystem.
    def get_system_row(self, system_id):
        self.cursor.execute("""
            SELECT
                id,
                system_type,
                full_covers,
                half_covers,
                rows
            FROM systems
            WHERE id= ?
        """, (system_id,))

        return self.cursor.fetchone()

    # Funktion som returnerar alla tipssystem som finns tillagda i databasen.
    def get_all_systems(self):
        self.cursor.execute("""
            SELECT id, system_type, full_covers, half_covers, row_count
            FROM systems            
        """)

        return self.cursor.fetchall()

    # Funktion som raderar ett tipssystem.
    def delete_system(self, system_id):
        # Antal vad som använder detta tipssystem.
        bet_count = self.get_bet_count_for_system(system_id)

        if bet_count > 0:
            raise ValueError(
                f"Systemet används av {bet_count} sparade "
                f"vad och kan därför inte raderas."
            )

        self.cursor.execute("""
            DELETE FROM systems
            WHERE id = ?
            """, (system_id,))

        self.connection.commit()
