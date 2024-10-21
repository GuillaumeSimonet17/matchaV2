import os
from flask import Flask
from dotenv import load_dotenv

from ORM.database import init_db
from routes import main as main_routes

app = Flask(__name__)

load_dotenv()

app.config['POSTGRES_DB'] = os.getenv('POSTGRES_DB')
app.config['POSTGRES_USER'] = os.getenv('POSTGRES_USER')
app.config['POSTGRES_PASSWORD'] = os.getenv('POSTGRES_PASSWORD')
app.config['POSTGRES_HOST'] = os.getenv('POSTGRES_HOST')
app.config['POSTGRES_PORT'] = os.getenv('POSTGRES_PORT')

init_db(app.config)
from ORM.tables.user import User

# user1 = User(None, 'usernae', 'last', 'firsty', 30, 'psd', 'ema', 'admiimgn', 'bio', 'gen', 'sexpr', fame_rate='fame')
# user1_id = user1.create()
# print('user1_id = ', user1_id[0])

# found = User.find_by_id(user1_id[0])
# print('found = ', found)
# print('id ', found.id)
# print('username = ', found.username)
# print('last_name = ', found.last_name)
# print('first_name = ', found.first_name)
# print('age = ', found.age)
# print('email = ', found.email)
# print('img = ', found.profile_image)
# print('bio = ', found.bio)
# print('gender = ', found.gender)
# print('gendpref', found.gender_pref)
# print('fame_rate', found.fame_rate)
# print('created_at', found.created_at)

app.register_blueprint(main_routes)

if __name__ == '__main__':
    app.run(debug=True)
