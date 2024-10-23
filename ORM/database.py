import psycopg2


class Database:
    def __init__(self, dbname, user, password, host, port):
        self.connection = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        print('Database connection established')
        self.cursor = self.connection.cursor()

    def execute(self, query, params=None, fetch=True):
        self.cursor.execute(query, params)
        if fetch:
            self.connection.commit()
            return self.cursor.fetchall()
        else:
            return self.connection.commit()

    # def close(self):
    #     self.cursor.close()
    #     self.connection.close()


db = None

def init_db(config):
    global db
    db = Database(config['POSTGRES_DB'], config['POSTGRES_USER'],
                  config['POSTGRES_PASSWORD'], config['POSTGRES_HOST'],
                  config['POSTGRES_PORT'])