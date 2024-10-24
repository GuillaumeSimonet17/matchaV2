from ORM.model import Model


class User(Model):
    table_name = 'app_user'
    column_names = ['id', 'username', 'last_name', 'first_name', 'age', 'password', 'email',
                    'profile_image', 'bio', 'gender', 'gender_pref', 'fame_rate', 'created_at']


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


    # ------------------------------------ READ
    @classmethod
    def _all(cls):
        try:
            results = cls.get_all_dicts()
            if results:
                return [cls(**row) for row in results]
        except Exception as e:
            raise e
        return None

    @classmethod
    def _find_by_id(cls, id):
        try:
            res = cls.get_dict_by_id(id)
            if res:
                return cls(**res)
        except Exception as e:
            raise e
        return None
