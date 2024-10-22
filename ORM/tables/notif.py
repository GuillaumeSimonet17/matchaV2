from ORM.model import Model
from ORM.database import db


class Notif(Model):
    table_name = 'notif'

    def __init__(self, id, state, sender_id, receiver_id, read, created_at):
        self.id = id
        self.state = state
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.read = read
        self.created_at = created_at
