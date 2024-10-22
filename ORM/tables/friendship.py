from ORM.model import Model
from ORM.database import db


class Friendship(Model):
    table_name = 'friendship'

    def __init__(self, id, state, sender_id, receiver_id, created_at):
        self.id = id
        self.state = state
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.created_at = created_at
