from typing import Any
from werkzeug.exceptions import NotFound
from ORM.database import db

class Model:
    table_name = ''
    column_names = None


    # ------------------------------------ CREATE
    def create(self):
        attrs = {key: value for key, value in self.__dict__.items() if key not in ['id', 'created_at']}
        columns = ', '.join(attrs.keys())
        placeholders = ', '.join(['%s'] * len(attrs))
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders}) RETURNING id;"
        values = tuple(attrs.values())
        try:
            # print('DB == ', db)
            res = db.execute(query, values)
            return res[0]
        except Exception as e:
            print('Error while creating table:', e)
            raise e

    # ------------------------------------ READ
    @classmethod
    def get_all_column_names(cls, columns: list[str] = None) -> list[str]:
        if columns:
            return columns
        if not cls.column_names:
            raise NotFound(f'No column names provided')
        return cls.column_names

    @classmethod
    def get_all_values(cls, columns: list[str] = None) -> tuple:
        columns = cls.get_all_column_names(columns)
        query = f"SELECT {', '.join(columns)} FROM {cls.table_name}"
        try:
            return db.execute(query)
        except Exception as e:
            raise e
    
    @classmethod
    def get_dicts_by_res(cls, res, columns: list[str] = None) -> list[dict[str, Any]]:
        datas = []
        for r in res:
            data = {}
            for idx, col_name in enumerate(columns):
                data[col_name] = r[idx]
            datas.append(data)
        return datas

    @classmethod
    def get_all_dicts(cls, columns: list[str] = None) -> list[dict[str, Any]]:
        columns = cls.get_all_column_names(columns)
        res = cls.get_all_values(columns)
        if res:
            datas = cls.get_dicts_by_res(res, columns)
            return datas

    @classmethod
    def get_values_by_id(cls, id: int, columns: list[str] = None) -> tuple:
        columns = cls.get_all_column_names(columns)
        query = f"SELECT {', '.join(columns)} FROM {cls.table_name} WHERE id = %s;"
        try:
            res = db.execute(query, (id,))
            if res:
                return res[0]
        except Exception as e:
            print(f"An error occurred: {e}")
            raise e
        raise NotFound(f'id {id} not found in {cls.table_name}')

    @classmethod
    def get_dict_by_id(cls, id: int, columns: list[str] = None) -> dict[str, Any]:
        columns = cls.get_all_column_names(columns)
        res = cls.get_values_by_id(id, columns)
        data = {}
        for idx, col_name in enumerate(columns):
            data[col_name] = res[idx]
        return data
    
    @classmethod
    def find_x_by_y(cls, y_name:str, y: int | str, columns: list[str] = None):
        columns = cls.get_all_column_names(columns)
        query = (f"SELECT {', '.join(columns)} FROM {cls.table_name} "
                 f"WHERE {y_name} = '{y}';")
        # print('query = ', query)
        try:
            res = db.execute(query)
            # print('res=>', res)

            if res:
                datas = cls.get_dicts_by_res(res, columns)
                # print('data = ', datas)
                return [cls(**row) for row in datas]
        except Exception as e:
            raise NotFound(f'id {id} not found in {cls.table_name}')
        return None

    # ------------------------------------ UPDATE
    def update(self, changes:dict[str, Any]) -> bool:
        for k in changes.keys():
            if k not in self.column_names:
                raise NotFound(f'Column name {k} is not in columns of {self.table_name}')
        set_clause = ', '.join([f"{key} = %s" for key in changes.keys() if key != 'id'])
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = %s;"
        values = tuple([v for k, v in changes.items() if k != 'id']) + (self.id,)
        try:
            db.execute(query, values, False)
            return True
        except Exception as e:
            print(f"An error occurred when updating: {e}")
            raise e
    
    @classmethod
    def update_mass(cls, changes:dict[str, Any], ids: [int]) -> bool:
        for k in changes.keys():
            if k not in cls.column_names:
                raise NotFound(f'Column name {k} is not in columns of {cls.table_name}')
        set_clause = ', '.join([f"{key} = %s" for key in changes.keys() if key != 'id'])
        query = f"UPDATE {cls.table_name} SET {set_clause} WHERE id IN ({', '.join(str(id) for id in ids)});"
        values = tuple([v for k, v in changes.items() if k != 'id'])
        try:
            db.execute(query, values, False)
            return True
        except Exception as e:
            print(f"An error occurred when updating in mass: {e}")
            raise e
    
    @classmethod
    def mark_as_read(cls, ids: [int]):
        ids_str = ', '.join(map(str, ids))
        query = f"UPDATE {cls.table_name} SET read = TRUE WHERE id IN ({ids_str});"
        try:
            db.execute(query, fetch=False)
        except Exception as e:
            print(f"An error occurred when marking as read: {e}")
            raise e

    # ------------------------------------ DELETE
    def delete(self):
        query = f"DELETE FROM {self.table_name} WHERE id = %s;"
        try:
            db.execute(query, (self.id,), False)
            return True
        except Exception as e:
            print(f"An error occurred when deleting: {e}")
            raise e
    
    @classmethod
    def delete_mass(cls, ids: [int]):
        query = f"DELETE FROM {cls.table_name} WHERE id IN ({', '.join(str(id) for id in ids)});"
        try:
            db.execute(query, fetch=False)
            return True
        except Exception as e:
            print(f"An error occurred when deleting in mass: {e}")
            raise e

