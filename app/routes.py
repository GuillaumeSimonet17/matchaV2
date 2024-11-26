from flask import Blueprint, flash, request, render_template, session, redirect, url_for, jsonify
from flask_socketio import emit, join_room

from managements.user_management.auth.login import auth_login
from managements.user_management.auth.register import auth_register
from managements.user_management.update_user import change_password

from managements.profile import go_profile
from managements.notif import go_notif
from managements.search import go_search
from managements.historic import go_historic
from managements.user_management.user import go_user
from managements.chat import go_chat

from ORM.tables.tag import Tag
from ORM.tables.friendship import Friendship
from ORM.views.profile import Profile
from ORM.tables.channel import Channel
from ORM.tables.message import Message
from ORM.tables.notif import Notif

from app import socketio

main = Blueprint('main', __name__)

# --------------------------- SOCKET ---------------------------

@socketio.on('join')
def on_join(data):
    user_id = data.get('user_id')
    print(user_id)
    if user_id:
        print('join => ', int(user_id))
        join_room(f"user_{user_id}")
        print(f"User {user_id} joined their room.")

# FRIENDSHIP ---------------
@socketio.on('send_invitation')
def send_invitation_route(data):
    sender_id = data.get('sender_id')
    receiver_id = data.get('receiver_id')

    # check if friendship exist
    friendship = Friendship.get_friendship_by_user_ids([sender_id, receiver_id])
    if friendship:
        if friendship.state == 'invitation':
            send_connection_route(data)
        return

    friendship = Friendship(None, 'invitation', sender_id, receiver_id)
    friendship.create()

    notif = Notif(None, 'invitation', sender_id, receiver_id, False)
    notif.create()
    
    sender = Profile._find_by_id(sender_id)
    
    emit('receive_invitation', {'sender_username': sender.username, 'sender_id': sender.id, 'date': 'Now', 'state': 'invitation' }, room=f'user_{receiver_id}')

@socketio.on('send_connection')
def send_connection_route(data):
    sender_id = data.get('sender_id')
    receiver_id = data.get('receiver_id')

    friendship = Friendship.get_friendship_by_user_ids([sender_id, receiver_id])

    # get friendship and check if state is invitation and receiver_id = sender_id
    if friendship.state != 'invitation' and friendship.sender_id != int(receiver_id):
        return

    # update state
    friendship.update({'state': 'connected'})

    # create channel between users
    channel = Channel(None, sender_id, receiver_id)
    channel.create()

    notif = Notif(None, 'connection', sender_id, receiver_id, False)
    notif.create()

    sender = Profile._find_by_id(sender_id)
    
    emit('receive_connection', {'sender_username': sender.username, 'sender_id': sender.id, 'date': 'Now', 'state': 'connected' }, room=f'user_{receiver_id}')

@socketio.on('send_uninvitation')
def send_uninvitation_route(data):
    sender_id = data.get('sender_id')
    receiver_id = data.get('receiver_id')

    # get friendship and check if state is connected
    friendship = Friendship.get_friendship_by_user_ids([sender_id, receiver_id])

    if friendship.state != 'connected':
        return

    # update state
    friendship.update({'state': 'uninvitation', 'sender_id': sender_id, 'receiver_id': receiver_id})

    notif = Notif(None, 'uninvitation', sender_id, receiver_id, False)
    notif.create()

    sender = Profile._find_by_id(sender_id)

    emit('receive_uninvitation', {'sender_username': sender.username, 'sender_id': sender.id, 'date': 'Now', 'state': 'uninvitation' }, room=f'user_{receiver_id}')

# CHAT ---------------
@socketio.on('get_messages')
def get_messages(data):
    user_id = session.get('user_id')
    profile_id = data.get('profile_id')
    
    profile_selected = Profile._find_by_id(profile_id)

    channel = Channel.find_channel_by_user_ids(user_id, profile_id)

    messages_data = []
    messages = Message.find_messages_by_channel_id(channel.id)

    if messages:
        messages_data = [{"receiver_id": msg.receiver_id, "sender_id": msg.sender_id, "content": msg.content,
                          "created_at": msg.created_at.strftime('%Y-%m-%d %H:%M') } for msg in messages]

    session['current_channel'] = profile_selected.id
    emit('display_messages', {'messages': messages_data, 'profile_username': profile_selected.username},
         room=request.sid)

@socketio.on('send_message')
def send_message(data):
    sender_id = int(data['sender_id'])
    receiver_id = int(data['receiver_id'])
    content = data['content']

    if receiver_id != 0:
        channel = Channel.find_channel_by_user_ids(sender_id, receiver_id)
        msg = Message(None, channel.id, sender_id, receiver_id, content, False)
        new_msg = msg.create()

    have_to_notif = False
    notifs_exist = Notif.find_notif('message', sender_id, receiver_id)
    if not notifs_exist:
        have_to_notif = True
    else:
        for notif_exist in notifs_exist:
            if notif_exist.read:
                have_to_notif = True

    if have_to_notif:
        notif = Notif(None, 'message', sender_id, receiver_id, False)
        notif.create()
        
    emit('receive_message', {'messages': new_msg, 'profile_id': sender_id}, room=f'user_{receiver_id}')

@socketio.on('received_message')
def received_message(data):
    if data['profile_id'] == session['current_channel']:
        get_messages(data)
    # else: add a notif

# --------------------------- HTTP ---------------------------

@main.route('/get_current_page')
def get_current_page():
    current_page = session.get('current_page', 'default')
    current_profile_id = session.get('profile_id', 'default')
    return jsonify({'current_page': current_page, 'current_profile_id': current_profile_id})

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if auth_login(request):
            return redirect(url_for('main.home'))
        flash('Ecris mieux stp', 'danger')
    
    if 'username' in session:
        session['current_page'] = 'home'
        return redirect(url_for('main.home'))
    return render_template('login.html')

@main.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('current_page', None)
    session.pop('current_channel', None)
    return redirect(url_for('main.login'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        return auth_register(request)
    tags = Tag._all()
    return render_template('register.html', tags=tags)

@main.route('/')
def home():
    print(session)
    if 'username' not in session:
        return redirect(url_for('main.login'))
    session['current_page'] = 'home'
    return go_search()

@main.route('/historic')
def historic():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    session['current_page'] = 'historic'
    return go_historic()

@main.route('/notifs', methods=['GET'])
def notifs():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    session['current_page'] = 'notifs'
    return go_notif()

@main.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    return go_chat()



@main.route('/profile/<int:profile_id>')
def profile(profile_id):
    if 'username' not in session:
        return redirect(url_for('main.login'))
    session['current_page'] = 'profile'
    return go_profile(profile_id)

@main.route('/user', methods=['GET', 'POST'])
def user():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    session['current_page'] = 'user'
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
