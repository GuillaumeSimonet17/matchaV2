from ORM.model import Model
from ORM.database import db

class User(Model):
    table_name = 'app_user'

    def __init__(self, id, username, last_name, first_name, age, password,
                 email, profile_image, bio, gender, gender_pref, fame_rate=None, created_at=None):
        self.id = id
        self.username = username
        self.last_name = last_name
        self.first_name = first_name
        self.age = age
        self.password = password
        self.email = email
        self.profile_image = profile_image
        self.bio = bio
        self.gender = gender
        self.gender_pref = gender_pref
        self.fame_rate = fame_rate
        self.created_at = created_at

    # @classmethod
    # def find_by_id(cls, id):
    #     query = f"SELECT * FROM {cls.table_name} WHERE id = %s;"
    #     print('QUERY: ', query)
    #     result = db.execute(query, (id,))
    #     print('result: ', result)
    #     print('*result[0]: ', *result[0])
    #     res = cls(*result[0]) if result else None
    #     print('RESID: ', res.id)
    #     print('RESUS: ', res.username)
    #     return res

    @classmethod
    def find_by_username(cls, username):
        query = f"SELECT * FROM {cls.table_name} WHERE username = %s;"
        result = db.execute(query, (username,))
        return cls(*result[0]) if result else None

