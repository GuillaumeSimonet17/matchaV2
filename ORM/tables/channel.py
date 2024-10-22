from ORM.model import Model


class Channel(Model):
    table_name = 'channel'
    column_names = ['id', 'user_a', 'user_b', 'created_at']


    def __init__(self, id, user_a, user_b, created_at=None):
        self.id = id
        self.user_a = user_a
        self.user_b = user_b
        self.created_at = created_at
