from ORM.database import db
from ORM.model import Model


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
        