from ORM.model import Model
from ORM.database import db


class Friendship(Model):
    table_name = 'friendship'
    column_names = ['id', 'state', 'sender_id', 'receiver_id', 'created_at']
    possible_states = ['invitation',  'uninvitation', 'connection']


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
                 f"WHERE state = {state} and receiver_id = {user_id} ;")
        res = db.execute(query)
        if not res:
            return None
        datas = cls.get_dicts_by_res(res, columns)
        return [cls(**row) for row in datas]

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
    def get_friendship_connections(cls, state: str, user_id: int, columns: list[str] = None):
        columns = cls.get_all_column_names(columns)
        query = (f"SELECT {', '.join(columns)} FROM {cls.table_name} "
                 f"WHERE state = {state} "
                 f"and (receiver_id = {user_id} or sender_id = {user_id});")
        res = db.execute(query)
        if not res:
            return None
        datas = cls.get_dicts_by_res(res, columns)
        return [cls(**row) for row in datas]

    @classmethod
    def get_friendship_by_user_ids(cls, user_ids: list[int], columns: list[str] = None):
        if len(user_ids) != 2:
            raise ValueError("It has to be 2 user_ids.")
        user1_id, user2_id = user_ids
        query = (f"SELECT {', '.join(columns)} FROM {cls.table_name} "
                 "WHERE (sender_id = %s AND receiver_id = %s) "
                 "OR (sender_id = %s AND receiver_id = %s);")
        res = db.execute(query, (user1_id, user2_id, user2_id, user1_id))
        return cls(**res[0])

    @classmethod
    def update_friendship_by_user_ids(cls, state: str, user_ids: list[int]):
        if len(user_ids) != 2:
            raise ValueError("It has to be 2 user_ids.")
        friendship = cls.get_friendship_by_user_ids(user_ids)
        query = (f"UPDATE {cls.table_name} SET state = {state} "
                 f"WHERE id IN {friendship.id}")
        res = db.execute(query)
        if not res:
            return None
        return True
