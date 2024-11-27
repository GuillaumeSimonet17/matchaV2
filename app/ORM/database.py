import psycopg2
import logging
import threading

db_lock = threading.Lock()


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
        with db_lock:
        
            try:
                logging.debug(f"Executing query: {query} with params: {params}")
                self.cursor.execute(query, params)
                if fetch:
                    result = self.cursor.fetchall()
                    logging.debug(f"Query result: {result}")
                    return result
                else:
                    self.connection.commit()
                    logging.debug("Query committed successfully.")
            except Exception as e:
                logging.error(f"Query failed: {e}")
                self.connection.rollback()
                raise e
        
    # def close(self):
    #     self.cursor.close()
    #     self.connection.close()


db = None

def init_db(config):
    global db
    print('Initializing database')
    db = Database(config['POSTGRES_DB'], config['POSTGRES_USER'],
                  config['POSTGRES_PASSWORD'], config['POSTGRES_HOST'],
                  config['POSTGRES_PORT'])
    return db
