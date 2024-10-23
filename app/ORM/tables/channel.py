from app.app import Model
from app.app import db


class Channel(Model):
    table_name = 'channel'
    column_names = ['id', 'user_a', 'user_b', 'created_at']


    def __init__(self, id, user_a, user_b, created_at=None):
        self.id = id
        self.user_a = user_a
        self.user_b = user_b
        self.created_at = created_at

    # ------------------------------------ READ
    @classmethod
    def _all(cls):
        try:
            results = cls.get_all_dicts()
            return [cls(**row) for row in results]
        except Exception as e:
            print(f"Erreur dans la methode all de User: {e}")
            return None

    @classmethod
    def _find_by_id(cls, id):
        try:
            res = cls.get_dict_by_id(id)
            return cls(**res)
        except Exception as e:
            print(f"Erreur dans la methode find_by_id de User: {e}")
            return None

    @classmethod
    def find_channels_by_user_id(cls, user_id: int, columns: list[str] = None):
        if user_id is None:
            raise ValueError('user_id cannot be None')
        columns = cls.get_all_column_names(columns)
        query = (f"SELECT {', '.join(columns)} FROM {cls.table_name} "
                 f"WHERE user_a = {user_id} or user_b = {user_id};")
        res = db.execute(query)
        if not res:
            return None
        datas = cls.get_dicts_by_res(res, columns)
        return [cls(**row) for row in datas]

    @classmethod
    def find_channel_by_user_ids(cls, user_1: int, user_2: int):
        query = (f"SELECT id FROM {cls.table_name} WHERE "
                 f"(user_a = {user_1} or user_a = {user_2}) "
                 f"and (user_b = {user_1} or user_b = {user_2});")
        res = db.execute(query)
        if not res:
            return None
        results = cls.get_dict_by_id(res[0])
        return [cls(**results)]
