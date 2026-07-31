from database.factories.entity_factory import EntityFactory


class Repository:
    def __init__(self, database):
        self.database = database
        self.connection = database.connection
        self.cursor = database.cursor
        self.factory = EntityFactory()
