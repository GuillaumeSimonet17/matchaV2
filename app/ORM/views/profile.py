import base64

from ORM.model import Model
from ORM.database import db


class Profile(Model):
    table_name = 'app_profile'
    column_names = ['id', 'username', 'last_name', 'first_name', 'age', 'profile_image',
                    'bio', 'gender', 'gender_pref', 'fame_rate']


    def __init__(self, id, username, last_name, first_name, age,
                 profile_image, bio, gender, gender_pref, fame_rate):
        self.id = id
        self.username = username
        self.last_name = last_name
        self.first_name = first_name
        self.age = age
        self.profile_image = profile_image
        self.bio = bio
        self.gender = gender
        self.gender_pref = gender_pref
        self.fame_rate = fame_rate

    # ------------------------------------ READ
    @classmethod
    def _all(cls):
        try:
            results = cls.get_all_dicts()
            return [cls(**row) for row in results]
        except Exception as e:
            print(f"Erreur dans la methode all de Profile: {e}")
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
    
    @classmethod
    def get_profile_image(cls, user_id):
        query = "SELECT profile_image FROM app_user WHERE id = %s;"
        image_data = db.execute(query, (user_id,))
        return base64.b64encode(image_data[0][0]).decode('utf-8')
