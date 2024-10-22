from ORM.database import db


class Model:
    table_name = ''

    def create(self):

        if self.table_name == 'app_user':
            if 'id' in self.__dict__:
                del self.__dict__['id']
            if 'created_at' in self.__dict__:
                del self.__dict__['created_at']
            if 'fame_rate' in self.__dict__:
                del self.__dict__['fame_rate']

        columns = ', '.join(self.__dict__.keys())
        placeholders = ', '.join(['%s'] * len(self.__dict__))
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders}) RETURNING id;"
        values = tuple(self.__dict__.values())
        return db.execute(query, values)

    def delete(self):
        query = f"DELETE FROM {self.table_name} WHERE id = %s;"
        values = tuple(self.__dict__['id'])
        return db.execute(query, values)

    def find_by_id(self, id):
        query = f"SELECT * FROM {self.table_name} WHERE id = %s;"
        return db.execute(query, (id,))

    def all(self):
        query = f"SELECT * FROM {self.table_name}"
        return db.execute(query)

    def update(self):
        set_clause = ', '.join([f"{key} = %s" for key in self.__dict__.keys() if key != 'id'])
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = %s;"
        values = tuple([v for k, v in self.__dict__.items() if k != 'id']) + (self.__dict__.get('id'),)
        return db.execute(query, values)