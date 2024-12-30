from ORM.model import Model
from ORM.database import db


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
            if results:
                return [cls(**row) for row in results]
        except Exception as e:
            raise e
        return None
        
    @classmethod
    def _find_by_id(cls, id: int):
        try:
            res = cls.get_dict_by_id(int(id))
            if res:
                return cls(**res)
        except Exception as e:
            return None
        return None

    @classmethod
    def _find_by_name(cls, name):
        try:
            res = cls.find_x_by_y('name', name, cls.column_names)
            if res:
                tag = res[0]
                return tag
        except Exception as e:
            print(e)
            return None
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
        return cls.find_x_by_y('user_id', user_id)
    
    @classmethod
    def find_user_tag_by_id(cls, user_id: int, tag_id: int, columns: list[str] = None):
        columns = cls.get_all_column_names(columns)
        query = (f"SELECT id FROM {cls.table_name} "
                 f"WHERE user_id = %s and tag_id = %s ;")
        try:
            id = db.execute(query, (user_id, tag_id))
            res = cls.get_dict_by_id(int(id[0][0]))
            if res:
                return cls(**res)
        except Exception as e:
            raise e
        return None