from ORM.database import db
from ORM.model import Model


class Message(Model):
    table_name = 'message'
    column_names = ['id', 'channel_id', 'sender_id', 'content', 'read', 'created_at']


    def __init__(self, id, channel_id, sender_id, content, read, created_at=None):
        self.id = id
        self.channel_id = channel_id
        self.sender_id = sender_id
        self.content = content
        self.read = read
        self.created_at = created_at


    @classmethod
    def find_messages_by_channel_id(cls, channel_id: int, columns: list[str] = None):
        return cls.find_x_by_y_id('channel_id', channel_id)

    # get last message => et ainsi vérifier "read"
    @classmethod
    def find_last_message_by_channel_id(cls, channel_id: int, columns: list[str] = None):
        columns = cls.get_all_column_names(columns)
        query = (f"SELECT {', '.join(columns)} FROM {cls.table_name} "
                 f"WHERE channel_id = {channel_id} "
                 f"ORDER BY created_at DESC LIMIT 1;")
        res = db.execute(query)
        if not res:
            return None
        data = cls.get_dicts_by_res(res, columns)
        return cls(**data[0])
