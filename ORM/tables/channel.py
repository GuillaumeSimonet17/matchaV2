from ORM.model import Model


class Channel(Model):
    table_name = 'channel'
    column_names = ['id', 'user_a', 'user_b', 'created_at']


    def __init__(self, id, user_a, user_b, created_at=None):
        self.id = id
        self.user_a = user_a
        self.user_b = user_b
        self.created_at = created_at

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
    def _find_channel_by_id(cls, id):
        try:
            res = cls.get_dict_by_id(id)
            return cls(**res)
        except Exception as e:
            print(f"Erreur dans la methode find_by_id de User: {e}")
            return None

    @classmethod
    def find_channels_by_user_id(cls, user_id: int):
        # Faire la requete ici
       # WHERE user_id == user_a or user_b
        pass

    @classmethod
    def find_channel_by_user_ids(cls, user_ids: list[int] = None):
       # WHERE user_ids[0] == user_a or user_b AND user_ids[1] == user_a or user_b
        pass