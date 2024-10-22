from typing import Any
from werkzeug.exceptions import NotFound
from ORM.database import db


class Model:
    table_name = ''
    column_names = None

    # ------------------------------------ CREATE
    def create(self):
        if self.table_name == 'app_user':
            if 'id' in self.__dict__:
                del self.__dict__['id']
            if 'created_at' in self.__dict__:
                del self.__dict__['created_at']
            if 'fame_rate' in self.__dict__:
                del self.__dict__['fame_rate']
        attrs = {key: value for key, value in self.__dict__.items() if key not in ['id', 'created_at']}
        columns = ', '.join(attrs.keys())
        placeholders = ', '.join(['%s'] * len(attrs))
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders}) RETURNING id;"
        values = tuple(attrs.values())
        res = db.execute(query, values)
        return res[0]

    # ------------------------------------ UTILS
    @classmethod
    def get_all_column_names(cls, columns: list[str] = None) -> list[str]:
        if columns:
            return columns
        if not cls.column_names:
            raise NotFound(f'No column names provided')
        return cls.column_names

    # ------------------------------------ READ
    @classmethod
    def get_all_values(cls, columns: list[str] = None) -> tuple:
        columns = cls.get_all_column_names(columns)
        query = f"SELECT {', '.join(columns)} FROM {cls.table_name}"
        return db.execute(query)
    
    @classmethod
    def get_all_dicts(cls, columns: list[str] = None) -> list[dict[str, Any]]:
        columns = cls.get_all_column_names(columns)
        res = cls.get_all_values(columns)
        print(res)
        datas = []
        print(columns)
        for r in res:
            data = {}
            for idx, col_name in enumerate(columns):
                data[col_name] = r[idx]
            datas.append(data)
        return datas

    @classmethod
    def get_values_by_id(cls, id: int, columns: list[str] = None) -> tuple:
        columns = cls.get_all_column_names(columns)
        query = f"SELECT {', '.join(columns)} FROM {cls.table_name} WHERE id = %s;"
        res = db.execute(query, (id,))
        if not res:
            raise NotFound(f'id {id} not found')
        return res[0]

    @classmethod
    def get_dict_by_id(cls, id: int, columns: list[str] = None) -> dict[str, Any]:
        columns = cls.get_all_column_names(columns)
        res = cls.get_values_by_id(id, columns)
        print(res)
        data = {}
        for idx, col_name in enumerate(columns):
            data[col_name] = res[idx]
        return data

    # ------------------------------------ UPDATE
    def update(self, **kwargs):
        print('UPDATE self.table_name = ', self.table_name)
        set_clause = ', '.join([f"{key} = %s" for key in kwargs.keys() if key != 'id'])
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = %s;"
        values = tuple([v for k, v in kwargs.items() if k != 'id']) + (kwargs['id'],)
        return db.execute(query, values)

    # ------------------------------------ DELETE
    def delete(self, id):
        print('DELETE self.table_name = ', self.table_name)
        query = f"DELETE FROM {self.table_name} WHERE id = %s;"
        return db.execute(query, (id,))
