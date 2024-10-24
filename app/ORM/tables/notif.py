from ORM.database import db
from ORM.model import Model


class Notif(Model):
    table_name = 'notif'
    column_names = ['id', 'state', 'sender_id', 'receiver_id', 'read', 'created_at']
    possible_states = ['message', 'invitation', 'connection', 'uninvitation', 'view']

    def __init__(self, id, state, sender_id, receiver_id, read, created_at=None):
        self.id = id
        if state not in self.possible_states:
            raise ValueError(f"State {state} is not valid")
        self.state = state
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.read = read
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
    def find_notifs_by_user(cls, receiver_id: int):
        return cls.find_x_by_y_id('receiver_id', receiver_id)

    @classmethod
    def mark_notifs_by_user_id_as_read(cls, user_id: int):
        notifs = cls.find_notifs_by_user(user_id)
        unread_notifs_ids = [notif.id for notif in notifs if not notif.read]
        if unread_notifs_ids:
            cls.mark_as_read(unread_notifs_ids)
