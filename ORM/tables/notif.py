from ORM.model import Model
from ORM.database import db


class Notif(Model):
    table_name = 'notif'
    column_names = ['id', 'state', 'sender_id', 'receiver_id', 'created_at']
    possible_states = ['message', 'invitation', 'connection', 'uninvitation', 'view']

    def __init__(self, id, state, sender_id, receiver_id, created_at=None):
        self.id = id
        if state not in self.possible_states:
            raise ValueError(f"State {state} is not valid")
        self.state = state
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.created_at = created_at

    @classmethod
    def _find_by_id(cls, id):
        try:
            res = cls.get_dict_by_id(id)
            return cls(**res)
        except Exception as e:
            print(f"Erreur dans la methode find_by_id de Notif: {e}")
            return None

    # si une notif existe deja même state et les memes ids dans l'ordre
    @classmethod
    def find_notif(cls, state: str, sender_id: int, receiver_id: int):
        if state not in cls.possible_states:
            raise ValueError(f"State {state} is not valid")
        query = (f"SELECT id FROM {cls.table_name} "
                 f"WHERE state = {state} and sender_id = {sender_id} and receiver_id = {receiver_id};")
        res = db.execute(query)
        if not res:
            return None
        results = cls.get_dict_by_id(res[0])
        return [cls(**results)]

    @classmethod
    def find_notifs_by_user(cls, receiver_id: int, columns: list[str] = None):
        columns = cls.get_all_column_names(columns)
        query = (f"SELECT {', '.join(columns)} FROM {cls.table_name} "
                 f"WHERE receiver_id = {receiver_id};")
        res = db.execute(query)
        if not res:
            return None
        datas = cls.get_dicts_by_res(res, columns)
        return [cls(**row) for row in datas]
