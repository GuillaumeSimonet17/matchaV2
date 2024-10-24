from ORM.database import db
from ORM.model import Model


class Tag(Model):
    table_name = 'tag'
    column_names = ['id', 'name']

    def __init__(self, id, name):
        self.id = id
        self.name = name


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
            print(f"Erreur dans la methode find_by_id de Notif: {e}")
            return None
    

class UserTag(Model):
    table_name = 'user_tag'
    column_names = ['id', 'user_id', 'tag_id']


    def __init__(self, id, user_id, tag_id):
        self.id = id
        self.user_id = user_id
        self.tag_id = tag_id


    @classmethod
    def find_tags_by_user_id(cls, user_id: int, columns: list[str] = None):
        if user_id is None:
            raise ValueError('user_id cannot be None')
        columns = cls.get_all_column_names(columns)
        query = (f"SELECT {', '.join(columns)} FROM {cls.table_name} "
                 f"WHERE user_id = {user_id};")
        res = db.execute(query)
        if not res:
            return None
        datas = cls.get_dicts_by_res(res, columns)
        return [cls(**row) for row in datas]