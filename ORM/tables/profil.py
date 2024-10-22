from ORM.model import Model
from ORM.database import db


class Profile(Model):
    table_name = 'profile'

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
