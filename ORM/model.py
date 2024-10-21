from ORM.database import db


class Model:
    table_name = ''

    def create(self):
        if self.table_name == 'app_user':
            if 'id' in self.__dict__:
                del self.__dict__['id']  # Supprimer l'ID pour l'insertion
            if 'created_at' in self.__dict__:
                del self.__dict__['created_at']  # Supprimer l'ID pour l'insertionfame_rate
            if 'fame_rate' in self.__dict__:
                del self.__dict__['fame_rate']  # Supprimer l'ID pour l'insertion

        columns = ', '.join(self.__dict__.keys())
        placeholders = ', '.join(['%s'] * len(self.__dict__))
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders}) RETURNING id;"
        values = tuple(self.__dict__.values())
        return db.execute(query, values)

    # def delete(self):
    #     columns = ', '.join(self.__dict__.keys())
    #
    # def all(self):
    #     query = f"SELECT * FROM {self.table_name}"
    #
    # def update(self):
    #     columns = ', '.join(self.__dict__.keys())