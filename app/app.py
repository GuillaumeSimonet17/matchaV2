import os

from flask import Flask
from flask_socketio import SocketIO
from dotenv import load_dotenv

from ORM.database import init_db

app = Flask(__name__)

app.config.update(
    SESSION_COOKIE_SAMESITE="None",  # Autoriser les cookies dans des contextes tiers
    SESSION_COOKIE_SECURE=True      # Obligatoire pour SameSite=None (HTTPS nécessaire)
)

socketio = SocketIO(app, cors_allowed_origins="*")

load_dotenv()

app.secret_key = os.getenv('SECRET_KEY')

app.config['POSTGRES_DB'] = os.getenv('POSTGRES_DB')
app.config['POSTGRES_USER'] = os.getenv('POSTGRES_USER')
app.config['POSTGRES_PASSWORD'] = os.getenv('POSTGRES_PASSWORD')
app.config['POSTGRES_HOST'] = os.getenv('POSTGRES_HOST')
app.config['POSTGRES_PORT'] = os.getenv('POSTGRES_PORT')

db = init_db(app.config)

from routes import main as main_routes

app.register_blueprint(main_routes)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
