from ORM.database import db
from ORM.model import Model


class Visit(Model):
    table_name = 'visit'
    column_names = ['id', 'sender_id', 'receiver_id', 'updated_at', 'created_at']


    def __init__(self, id, sender_id, receiver_id, updated_at=None, created_at=None):
        self.id = id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.updated_at = updated_at
        self.created_at = created_at


    @classmethod
    def _find_by_id(cls, id: int):
        try:
            res = cls.get_dict_by_id(int(id))
            if res:
                return cls(**res)
        except Exception as e:
            raise e
        return None

    @classmethod
    def find_visit(cls, sender_id: int, receiver_id: int):
        query = (f"SELECT id FROM {cls.table_name} "
                 f"WHERE sender_id = {sender_id} and receiver_id = {receiver_id};")
        try:
            res = db.execute(query)
            if res:
                results = cls.get_dict_by_id(res[0])
                return [cls(**results)]
        except Exception as e:
            raise e
        return None

    @classmethod
    def find_visits_by_user(cls, sender_id: int, columns: list[str] = None):
        return cls.find_x_by_y('sender_id', sender_id)
