import psycopg2
import base64

from ORM.model import Model
from ORM.database import db

class User(Model):
    table_name = 'app_user'
    column_names = ['id', 'username', 'last_name', 'first_name', 'age', 'password', 'email',
                    'profile_image', 'bio', 'gender', 'gender_pref', 'fame_rate', 'connected',
                    'location', 'lng', 'lat', 'created_at']


    def __init__(self, id, username, last_name, first_name, age, password,
                 email, profile_image, bio, gender, gender_pref, fame_rate, connected, location, lng, lat, created_at=None):
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
        self.connected = connected
        self.location = location
        self.lng = lng
        self.lat = lat
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
    def _find_by_id(cls, id: int):
        try:
            res = cls.get_dict_by_id(int(id))
            if res:
                return cls(**res)
        except Exception as e:
            raise e
        return None
    
    @classmethod
    def _find_by_username(cls, username):
        try:
            res = cls.find_x_by_y('username', username, cls.column_names)
            if res:
                usr = res[0]
                # print(usr)
                return usr
        except Exception as e:
            print(e)
            return None
        return None

    @classmethod
    def save_profile_image(cls, user_id, image_data):
        query = "UPDATE app_user SET profile_image = %s WHERE id = %s;"
        try:
            db.execute(query, (psycopg2.Binary(image_data), user_id), fetch=False)
        except Exception as e:
            print(e)
            return None
        return True

    @classmethod
    def get_profile_image(cls, user_id):
        query = f"SELECT profile_image FROM app_user WHERE id = {user_id};"
        image_data = db.execute(query)
        return base64.b64encode(image_data[0][0]).decode('utf-8')
