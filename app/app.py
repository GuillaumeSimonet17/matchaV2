import os

from flask import Flask
from flask_socketio import SocketIO
from dotenv import load_dotenv
from flask_mail import Mail

from ORM.database import init_db

from itsdangerous import URLSafeTimedSerializer

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

app.config['MAIL_SERVER']="localhost"
app.config['MAIL_PORT'] = 1025
app.config['MAIL_USERNAME'] = "guillaume@gmail.com"
app.config['MAIL_PASSWORD'] = "your_email_password"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)
serializer = URLSafeTimedSerializer(app.secret_key)

db = init_db(app.config)

from routes import main as main_routes

app.register_blueprint(main_routes)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
