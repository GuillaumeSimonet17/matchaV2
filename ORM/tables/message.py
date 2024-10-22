from ORM.model import Model
from ORM.database import db


class Message(Model):
    table_name = 'message'
    column_names = ['id', 'channel_id', 'sender_id', 'content', 'read', 'created_at']


    def __init__(self, id, channel_id, sender_id, content, read, created_at):
        self.id = id
        self.channel_id = channel_id
        self.sender_id = sender_id
        self.content = content
        self.read = read
        self.created_at = created_at
