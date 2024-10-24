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
            if results:
                return [cls(**row) for row in results]
        except Exception as e:
            raise e
        return None
        
    @classmethod
    def _find_by_id(cls, id):
        try:
            res = cls.get_dict_by_id(id)
            if res:
                return cls(**res)
        except Exception as e:
            raise e
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
        return cls.find_x_by_y_id('user_id', user_id)
