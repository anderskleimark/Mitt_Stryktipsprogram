from database.repositories.repository import Repository


class CountryRepository(Repository):
    """
        Repository för databashantering av länder.
    """

    def __init__(self, database):
        """
            Initierar klassen.
        """
        super().__init__(database)

    def get_all_countries(self):
        """
            Hämtar alla länder från databasen.
            Returnerar en lista med Country-objekt.
        """
        self.cursor.execute(
            """
                SELECT  id AS country_id,
                        country_name,
                        iso_code AS country_code
                FROM countries
            """
        )

        rows = self.cursor.fetchall()
        countries = []
        for row in rows:
            country = self.factory.create_country(row)
            countries.append(country)

        return countries
