from app.app import Model


class Friendship(Model):
    table_name = 'friendship'
    column_names = ['id', 'state', 'sender_id', 'receiver_id', 'created_at']


    def __init__(self, id, state, sender_id, receiver_id, created_at):
        self.id = id
        self.state = state
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.created_at = created_at
