from database.repositories.repository import Repository


class SettingRepository(Repository):
    """
        Klass för hantering av inställningar i databasen.
    """

    def get_setting(self, key):
        self.cursor.execute(
            """
                SELECT                                        
                    setting_value
                FROM settings
                WHERE setting_key = ?
            """,
            (
                key,
            )
        )
        row = self.cursor.fetchone()
        if not row:
            return None
        return row["setting_value"]

    def set_setting(self, key, value):
        """
            Skapar eller uppdaterar en inställning.
        """
        self.cursor.execute(
            """
            INSERT INTO settings (
                setting_key,
                setting_value
            )
            VALUES (?, ?)
            ON CONFLICT(setting_key)
            DO UPDATE SET
                setting_value = excluded.setting_value
            """,
            (
                key,
                value
            )
        )

        self.connection.commit()
