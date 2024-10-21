import app
from flask import Blueprint, render_template


main = Blueprint('main', __name__)


@main.route('/')
def home():
    return render_template('search.html')

@main.route('/chat')
def chat():
    return render_template('chat.html')

@main.route('/historic')
def historic():
    return render_template('historic.html')

@main.route('/notifs')
def notifs():
    return render_template('notifs.html')

@main.route('/profile')
def profile():
    return render_template('profile.html')

@main.route('/user')
def user():
    return render_template('user.html')
