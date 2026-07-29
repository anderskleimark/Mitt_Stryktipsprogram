from database.repositories.repository import Repository


class CountryRepository(Repository):
    def __init__(self, database):
        super().__init__(database)

    def get_all_countries(self):
        self.cursor.execute("""
            SELECT id, country_name, iso_code
            FROM countries
            ORDER BY country_name
        """)
        return self.cursor.fetchall()
