from app.app import Model
from app.app import db


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
    def _find_by_id(cls, id):
        try:
            res = cls.get_dict_by_id(id)
            return cls(**res)
        except Exception as e:
            print(f"Erreur dans la methode find_by_id de Notif: {e}")
            return None

    @classmethod
    def find_visit(cls, sender_id: int, receiver_id: int):
        query = (f"SELECT id FROM {cls.table_name} "
                 f"WHERE sender_id = {sender_id} and receiver_id = {receiver_id};")
        res = db.execute(query)
        if not res:
            return None
        results = cls.get_dict_by_id(res[0])
        return [cls(**results)]

    @classmethod
    def find_visits_by_user(cls, sender_id: int, columns: list[str] = None):
        columns = cls.get_all_column_names(columns)
        query = (f"SELECT {', '.join(columns)} FROM {cls.table_name} "
                 f"WHERE sender_id = {sender_id};")
        res = db.execute(query)
        if not res:
            return None
        datas = cls.get_dicts_by_res(res, columns)
        return [cls(**row) for row in datas]
