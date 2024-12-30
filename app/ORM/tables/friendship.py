from ORM.model import Model
from ORM.database import db


class Friendship(Model):
    table_name = 'friendship'
    column_names = ['id', 'state', 'sender_id', 'receiver_id', 'created_at']
    possible_states = ['invitation',  'uninvitation', 'connected']


    def __init__(self, id, state, sender_id, receiver_id, created_at=None):
        self.id = id
        self.state = state
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.created_at = created_at


    @classmethod
    def select_where_and(cls, state: str, user_id: int, columns: list[str] = None):
        if state not in cls.possible_states:
            raise ValueError("It has to be one of the possible states.")
        columns = cls.get_all_column_names(columns)
        query = (f"SELECT {', '.join(columns)} FROM {cls.table_name} "
                 f"WHERE state = %s and receiver_id = %s ;")
        
        try:
            res = db.execute(query, (state, user_id))
            if res:
                datas = cls.get_dicts_by_res(res, columns)
                return [cls(**row) for row in datas]
        except Exception as e:
            raise e
        return None

    # --- pending ---
    @classmethod
    def get_invitations_received(cls, receiver_id: int):
        return cls.select_where_and('invitation', receiver_id)

    @classmethod
    def get_invitations_send(cls, sender_id: int):
        return cls.select_where_and('invitation', sender_id)

    @classmethod
    def get_uninvitations_received(cls, receiver_id: int):
        return cls.select_where_and('uninvitation', receiver_id)
    
    @classmethod
    def get_friendship_uninvitations_send(cls, sender_id: int):
        return cls.select_where_and('uninvitation', sender_id)

    @classmethod
    def get_friendship_connections(cls, user_id: int, columns: list[str] = None):
        columns = cls.get_all_column_names(columns)
        query = (f"SELECT {', '.join(columns)} FROM {cls.table_name} "
                 f"WHERE state = 'connected' "
                 f"and (receiver_id = %s or sender_id = %s);")
        try:
            res = db.execute(query, (user_id, user_id))
            if res:
                datas = cls.get_dicts_by_res(res, columns)
                return [cls(**row) for row in datas]
        except Exception as e:
            raise e
        return None

    @classmethod
    def get_friendship_by_user_ids(cls, user_ids: list[int], columns: list[str] = None):
        if len(user_ids) != 2:
            raise ValueError("It has to be 2 user_ids.")
        columns = cls.get_all_column_names(columns)
        query = (f"SELECT {', '.join(columns)} FROM {cls.table_name} "
                 f"WHERE (sender_id = %s AND receiver_id = %s) "
                 f"OR (sender_id = %s AND receiver_id = %s);")
        try:
            res = db.execute(query, (user_ids[0], user_ids[1], user_ids[1], user_ids[0]))
            if res:
                dict = cls.get_dict_by_id(res[0][0])
                return cls(**dict)
        except Exception as e:
            raise e
        return None

    @classmethod
    def update_friendship_by_user_ids(cls, state: str, user_ids: list[int]):
        if len(user_ids) != 2:
            raise ValueError("It has to be 2 user_ids.")
        friendship = cls.get_friendship_by_user_ids(user_ids)
        if friendship:
            query = (f"UPDATE {cls.table_name} SET state = %s "
                     f"WHERE id = {friendship.id}")
            try:
                db.execute(query, (state, ), fetch=False)
            except Exception as e:
                raise e
        return None
