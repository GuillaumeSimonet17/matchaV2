from ORM.model import Model
from ORM.database import db


class View(Model):
    table_name = 'view'
    column_names = ['id', 'sender_id', 'receiver_id', 'created_at']

    def __init__(self, id, sender_id, receiver_id, created_at):
        self.id = id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.created_at = created_at
