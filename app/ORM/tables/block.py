from ORM.model import Model
from ORM.database import db


class Block(Model):
    table_name = 'block'
    column_names = ['id', 'sender_id', 'receiver_id', 'created_at']
    
    def __init__(self, id, sender_id, receiver_id, created_at=None):
        self.id = id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.created_at = created_at
    
    @classmethod
    def find_block(cls, sender_id: int, receiver_id: int):
        query = (f"SELECT id FROM {cls.table_name} "
                 f"WHERE sender_id = {sender_id} and receiver_id = {receiver_id};")
        try:
            res = db.execute(query)
            if res:
                return True
        except Exception as e:
            raise e
        return None

    @classmethod
    def find_blocks_by_receiver_id(cls, receiver_id: int, columns=None):
        columns = cls.get_all_column_names(columns)
        query = (f"SELECT {', '.join(columns)} FROM {cls.table_name} "
                 f"WHERE receiver_id = {receiver_id};")
        try:
            res = db.execute(query)
            if res:
                datas = cls.get_dicts_by_res(res, columns)
                return [cls(**row) for row in datas]
        except Exception as e:
            raise e
        return None


    @classmethod
    def find_blocks_by_user_id(cls, user_id: int, columns=None):
        columns = cls.get_all_column_names(columns)
        query = (f"SELECT {', '.join(columns)} FROM {cls.table_name} "
                 f"WHERE receiver_id = {user_id} or sender_id = {user_id};")
        try:
            res = db.execute(query)
            if res:
                datas = cls.get_dicts_by_res(res, columns)
                return [cls(**row) for row in datas]
        except Exception as e:
            raise e
        return None
