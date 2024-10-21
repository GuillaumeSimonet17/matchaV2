import os
from flask import Flask, render_template
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

app.config['POSTGRES_DB'] = os.getenv('POSTGRES_DB')
app.config['POSTGRES_USER'] = os.getenv('POSTGRES_USER')
app.config['POSTGRES_PASSWORD'] = os.getenv('POSTGRES_PASSWORD')
app.config['POSTGRES_HOST'] = os.getenv('POSTGRES_HOST')
app.config['POSTGRES_PORT'] = os.getenv('POSTGRES_PORT')

@app.route('/')
def home():
    return render_template('search.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/historic')
def historic():
    return render_template('historic.html')

@app.route('/notifs')
def notifs():
    return render_template('notifs.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/user')
def user():
    return render_template('user.html')


if __name__ == '__main__':
    app.run(debug=True)
