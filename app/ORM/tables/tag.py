from app.app import Model


class Tag(Model):
    table_name = 'tag'


    def __init__(self, id, name):
        self.id = id
        self.name = name


class UserTag(Model):
    table_name = 'user_tag'
    column_names = ['id', 'user_id', 'tag_id']


    def __init__(self, id, user_id, tag_id):
        self.id = id
        self.user_id = user_id
        self.tag_id = tag_id