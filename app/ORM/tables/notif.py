from ORM.database import db
from ORM.model import Model


class Notif(Model):
    table_name = 'notif'
    column_names = ['id', 'state', 'sender_id', 'receiver_id', 'read', 'created_at']
    possible_states = ['message', 'invitation', 'uninvitation', 'connection', 'view']
    
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
    def _find_by_id(cls, id: int):
        try:
            res = cls.get_dict_by_id(id)
            if res:
                return cls(**res)
        except Exception as e:
            raise e
        return None
    
    # si une notif existe deja même state et les memes ids dans l'ordre
    @classmethod
    def find_notif(cls, state: str, sender_id: int, receiver_id: int):
        if state not in cls.possible_states:
            raise ValueError(f"State {state} is not valid")
        query = (f"SELECT id FROM {cls.table_name} "
                 f"WHERE state = %s and sender_id = %s and receiver_id = %s ;")
        try:
            res = db.execute(query, (state, sender_id, receiver_id))
            if res or len(res) > 0:
                results = cls.get_dict_by_id(res[0])
                
                return [cls(**results)]
        except Exception as e:
            raise e
        return None
   
    @classmethod
    def find_notifs(cls, state: str, sender_id: int, receiver_id: int, columns: list[str] = None):
        if state not in cls.possible_states:
            raise ValueError(f"State {state} is not valid")
        columns = cls.get_all_column_names(columns)
        query = (f"SELECT {', '.join(columns)} FROM {cls.table_name} "
                 f"WHERE state = %s and sender_id = %s and receiver_id = %s ;")
        try:
            res = db.execute(query, (state, sender_id, receiver_id))
            if res:
                datas = cls.get_dicts_by_res(res, columns)
                return [cls(**row) for row in datas]
        except Exception as e:
            raise e
        return None

    @classmethod
    def find_notifs_by_user(cls, receiver_id: int):
        return cls.find_x_by_y('receiver_id', receiver_id)
    
    @classmethod
    def mark_notifs_by_user_id_as_read(cls, user_id: int):
        notifs = cls.find_notifs_by_user(user_id)
        if notifs:
            unread_notifs_ids = [notif.id for notif in notifs if not notif.read and notif.state != 'message']
            if unread_notifs_ids:
                cls.mark_as_read(unread_notifs_ids)
    
    @classmethod
    def delete_notifs_msg_by_user_id(cls, user_id: int):
        notifs = cls.find_notifs_by_user(user_id)
        if notifs:
            msg_notifs_ids = [notif.id for notif in notifs if notif.state == 'message']
            if msg_notifs_ids:
                cls.delete_mass(msg_notifs_ids)
