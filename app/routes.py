from flask import Blueprint, flash, request, render_template, session, redirect, url_for
from flask_socketio import emit, join_room


from managements.user_management.auth.login import auth_login
from managements.user_management.auth.register import auth_register
from managements.user_management.update_user import change_password

from managements.profile import go_profile
from managements.notif import go_notif
from managements.search import go_search
from managements.historic import go_historic
from managements.user_management.user import go_user

from ORM.tables.tag import Tag

from app import socketio

main = Blueprint('main', __name__)

# --------------------------- SOCKET ---------------------------

@socketio.on('join')
def on_join(data):
    user_id = data.get('user_id')
    if user_id:
        join_room(user_id)
        print(f"User {user_id} joined their room.")

@socketio.on('send_invitation')
def send_invitation_route(data):
    sender_id = data.get('sender_id')
    receiver_id = data.get('receiver_id')
    print('ca envoi sa mér', sender_id, receiver_id)
    emit('receive_invitation', {'message': f'Invitation sent from {sender_id}'}, room=receiver_id)


# --------------------------- HTTP ---------------------------

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if auth_login(request):
            return redirect(url_for('main.home'))
        flash('Ecris mieux stp', 'danger')
    
    if 'username' in session:
        return redirect(url_for('main.home'))
    return render_template('login.html')

@main.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('main.login'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        return auth_register(request)
    tags = Tag._all()
    return render_template('register.html', tags=tags)

@main.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    return go_search()

@main.route('/historic')
def historic():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    return go_historic()

@main.route('/notifs', methods=['GET'])
def notifs():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    return go_notif()

@main.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    return render_template('chat.html')

@main.route('/profile/<int:profile_id>')
def profile(profile_id):
    if 'username' not in session:
        return redirect(url_for('main.login'))
    return go_profile(profile_id)

@main.route('/user', methods=['GET', 'POST'])
def user():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    return go_user()

@main.route('/change-password', methods=['POST'])
def update_password():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    change_password(request)
    return redirect(url_for('main.user'))

@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
