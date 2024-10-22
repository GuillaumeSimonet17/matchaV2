from typing import Any
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

    # ------------------------------------ CREATE
    def _create(self):
        try:
            return super().create()
        except Exception as e:
            print(f"Erreur dans la methode create de User: {e}")
            return None

    # ------------------------------------ READ
    @classmethod
    def _all(cls):
        try:
            results = cls.get_all_dicts()
            return [cls(**row) for row in results]
        except Exception as e:
            print(f"Erreur dans la methode all de User: {e}")
            return None

    @classmethod
    def _find_by_id(cls, id):
        try:
            res = cls.get_dict_by_id(id)
            return cls(**res)
        except Exception as e:
            print(f"Erreur dans la methode find_by_id de User: {e}")
            return None

    # ------------------------------------ UPDATE
    def _update_infos(self, vals_dict):
        try:
            if 'id' not in vals_dict:
                raise ValueError("L'ID doit être inclus dans vals_dict.")

            super().update(**vals_dict)
            return True
        except Exception as e:
            print(f"Erreur dans la methode update de User: {e}")
            return None

    # ------------------------------------ DELETE
    def _delete(self, id):
        try:
            result = super().delete(id)
            return result
        except Exception as e:
            print(f"Erreur dans la méthode delete de User: {e}")
            return None