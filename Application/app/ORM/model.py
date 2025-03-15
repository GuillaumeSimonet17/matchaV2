from typing import Any
from werkzeug.exceptions import NotFound
from ORM.database import db
import logging

logger = logging.getLogger(__name__)


class Model:
    table_name = ''
    column_names = None
    
    # ------------------------------------ CREATE
    def create(self):
        attrs = {key: value for key, value in self.__dict__.items() if key not in ['id', 'created_at']}
        if not attrs:
            raise ValueError("No valid attributes to insert.")
        
        columns = ', '.join(attrs.keys())
        placeholders = ', '.join(['%s'] * len(attrs))
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders}) RETURNING id;"
        values = tuple(attrs.values())
        
        try:
            db.execute(query, values, fetch=False)
            return True
        except Exception as e:
            logger.error("Erreur lors de l'insertion dans la table %s: %s", self.table_name, e)
            raise RuntimeError(f"Failed to insert data into table {self.table_name}.") from e
    
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
        valid_columns = cls.get_all_column_names(columns)
        if columns:
            invalid_columns = [col for col in columns if col not in valid_columns]
            if invalid_columns:
                raise ValueError(f"Invalid columns specified: {', '.join(invalid_columns)}")
        else:
            columns = valid_columns

        query = f"SELECT {', '.join(columns)} FROM {cls.table_name};"
        try:
            return db.execute(query)
        except Exception as e:
            logger.error("Erreur lors de la récupération des données de la table '%s': %s", cls.table_name, e)
            raise RuntimeError(f"Failed to fetch data from table {cls.table_name}.") from e
    
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
        valid_columns = cls.get_all_column_names(columns)
        if columns:
            invalid_columns = [col for col in columns if col not in valid_columns]
            if invalid_columns:
                raise ValueError(f"Invalid columns specified: {', '.join(invalid_columns)}")
        else:
            columns = valid_columns

        res = cls.get_all_values(columns)
        if res:
            datas = cls.get_dicts_by_res(res, columns)
            return datas
    
    @classmethod
    def get_values_by_id(cls, id: int, columns: list[str] = None) -> tuple:
        valid_columns = cls.get_all_column_names(columns)
        if columns:
            invalid_columns = [col for col in columns if col not in valid_columns]
            if invalid_columns:
                raise ValueError(f"Invalid columns specified: {', '.join(invalid_columns)}")
        else:
            columns = valid_columns
        
        query = f"SELECT {', '.join(columns)} FROM {cls.table_name} WHERE id = %s;"
        try:
            res = db.execute(query, (id,))
            if res:
                return res[0]
        except Exception as e:
            logger.error("Erreur lors de la récupération de l'enregistrement avec ID '%s' dans '%s': %s",
                         id, cls.table_name, e)
            raise RuntimeError(f"Failed to fetch record with ID {id} from table {cls.table_name}.") from e

    @classmethod
    def get_dict_by_id(cls, id: int, columns: list[str] = None) -> dict[str, Any] | None:
        valid_columns = cls.get_all_column_names(columns)
        if columns:
            invalid_columns = [col for col in columns if col not in valid_columns]
            if invalid_columns:
                raise ValueError(f"Invalid columns specified: {', '.join(invalid_columns)}")
        else:
            columns = valid_columns

        res = cls.get_values_by_id(id, columns)
        if not res:
            return None
        data = {}
        for idx, col_name in enumerate(columns):
            data[col_name] = res[idx]
        return data

    @classmethod
    def find_x_by_y(cls, y_name: str, y: int | str, columns: list[str] = None):
        valid_columns = cls.get_all_column_names(columns)
        if columns:
            invalid_columns = [col for col in columns if col not in valid_columns]
            if invalid_columns:
                raise ValueError(f"Invalid columns specified: {', '.join(invalid_columns)}")
        else:
            columns = valid_columns

        query = (f"SELECT {', '.join(columns)} FROM {cls.table_name} "
                 f"WHERE {y_name} = %s;")
        try:
            res = db.execute(query, (y,))

            if res:
                datas = cls.get_dicts_by_res(res, columns)
                if datas:
                    return [cls(**row) for row in datas]
        except Exception as e:
            logger.error("Erreur lors de la recherche dans la table %s avec %s = %s : %s",
                         cls.table_name, y_name, y, e)
            raise RuntimeError(f"Failed to fetch records from {cls.table_name}.") from e
        return None

    # ------------------------------------ UPDATE
    def update(self, changes: dict[str, Any]) -> bool:
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
            db.execute(query, (self.id,), fetch=False)
            return True
        except Exception as e:
            logger.error("Error deleting record with ID %s from table %s: %s", self.id, self.table_name, e)
            raise RuntimeError(f"Failed to delete record with ID {self.id}.") from e

    @classmethod
    def delete_mass(cls, ids: [int]):
        if not ids or not all(isinstance(id, int) for id in ids):
            raise ValueError("IDs must be a non-empty list of integers.")
        
        placeholders = ', '.join(['%s'] * len(ids))
        query = f"DELETE FROM {cls.table_name} WHERE id IN ({placeholders});"
        try:
            db.execute(query, tuple(ids), fetch=False)
            return True
        except Exception as e:
            print(f"An error occurred when deleting in mass: {e}")
            raise e
