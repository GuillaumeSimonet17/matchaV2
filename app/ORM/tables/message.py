from ORM.database import db
from ORM.model import Model


class Message(Model):
    table_name = 'message'
    column_names = ['id', 'channel_id', 'sender_id', 'receiver_id', 'content', 'read', 'created_at']


    def __init__(self, id, channel_id, sender_id, receiver_id, content, read, created_at=None):
        self.id = id
        self.channel_id = channel_id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content
        self.read = read
        self.created_at = created_at


    @classmethod
    def find_messages_by_channel_id(cls, channel_id: int):
        return cls.find_x_by_y('channel_id', channel_id)

    @classmethod
    def find_receiver_messages_by_channel_id(cls, channel_id: int, receiver_id: int, columns: list[str] = None):
        columns = cls.get_all_column_names(columns)
        query = (f"SELECT {', '.join(columns)} FROM {cls.table_name} "
                 f"WHERE channel_id = %s and receiver_id = %s ;")
        try:
            messages = db.execute(query, (channel_id, receiver_id))
            if messages:
                datas = cls.get_dicts_by_res(messages, columns)
                return [cls(**row) for row in datas]
        except Exception as e:
            raise e
        return None

    @classmethod
    def mark_messages_as_read(cls, channel_id: int, receiver_id: int):
        my_messages = cls.find_receiver_messages_by_channel_id(channel_id, receiver_id)
        if my_messages:
            unread_messages_ids = [message.id for message in my_messages if not message.read]
            if unread_messages_ids:
                cls.mark_as_read(unread_messages_ids)

    # get last message => et ainsi vérifier "read"
    # si sender_id c'est moi, alors pas de notif, si receiver_id c'est moi et read=False, alors notif
    @classmethod
    def find_last_message_by_channel_id(cls, channel_id: int, columns: list[str] = None):
        columns = cls.get_all_column_names(columns)
        query = (f"SELECT {', '.join(columns)} FROM {cls.table_name} "
                 f"WHERE channel_id = %s "
                 f"ORDER BY created_at DESC LIMIT 1;")
        try:
            res = db.execute(query, (channel_id, ))
            if res:
                data = cls.get_dicts_by_res(res, columns)
                return cls(**data[0])
        except Exception as e:
            raise e
        return None
    
    @classmethod
    def find_last_channel_id(cls, user_id: int):
        query = (f"SELECT sender_id, receiver_id, channel_id FROM {cls.table_name} "
                 f"WHERE sender_id = %s or receiver_id = %s "
                 f"ORDER BY created_at DESC LIMIT 1;")
        try:
            res = db.execute(query, (user_id, user_id))
            if res:
                if user_id == res[0][0]:
                    return {'profile_id': res[0][1], 'channel_id': res[0][2]}
                else:
                    return {'profile_id': res[0][0], 'channel_id': res[0][2]}
        except Exception as e:
            raise e
        return None
