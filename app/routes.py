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
from ORM.tables.friendship import Friendship
from ORM.views.profile import Profile
from ORM.tables.channel import Channel
from ORM.tables.message import Message

from app import socketio

main = Blueprint('main', __name__)

# --------------------------- SOCKET ---------------------------

@socketio.on('join')
def on_join(data):
    user_id = data.get('user_id')
    if user_id:
        join_room(user_id)
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

    # create friendship
    friendship = Friendship(None, 'invitation', sender_id, receiver_id)
    friendship.create()

    # add notif

    emit('receive_invitation', {'message': f'Invitation sent from {sender_id}'}, room=receiver_id)

@socketio.on('send_connection')
def send_connection_route(data):
    sender_id = data.get('sender_id')
    receiver_id = data.get('receiver_id')

    # get friendship and check if state is invitation and receiver_id = sender_id
    friendship = Friendship.get_friendship_by_user_ids([sender_id, receiver_id])
    
    if friendship.state != 'invitation' and friendship.sender_id != int(receiver_id):
        return

    # update state
    friendship.update({'state': 'connected'})

    # create channel between users
    channel = Channel(None, sender_id, receiver_id)
    channel.create()

    # add notif

    emit('receive_connection', {'message': f'Connection sent from {sender_id}'}, room=receiver_id)

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
    
    # add notif

    emit('receive_uninvitation', {'message': f'Uninvitation sent from {sender_id}'}, room=receiver_id)

# CHAT ---------------
@socketio.on('get_messages')
def get_messages(data):
    user_id = session.get('user_id')
    profile_id = data.get('profile_id')
    
    profile_selected = Profile._find_by_id(profile_id)

    # Récupérer le channel
    channel = Channel.find_channel_by_user_ids(user_id, profile_id)

    # Récupérer les messages entre user_id et profile_id
    messages_data = []
    messages = Message.find_messages_by_channel_id(channel.id)

    if messages:
        messages_data = [{"receiver_id": msg.receiver_id, "sender_id": msg.sender_id, "content": msg.content, "created_at": msg.created_at.strftime('%Y-%m-%d %H:%M') } for msg in messages]

    # Envoyer les messages au client qui a demandé
    emit('display_messages', {'messages': messages_data, 'profile_username': profile_selected.username}, room=request.sid)

@socketio.on('send_message')
def send_message(data):
    print(data)
    sender_id = int(data['sender_id'])
    receiver_id = int(data['receiver_id'])
    content = data['content']
    print(content)
    print(type(sender_id))
    print(receiver_id)
    if receiver_id != 0:
        channel = Channel.find_channel_by_user_ids(sender_id, receiver_id)
        msg = Message(None, channel.id, sender_id, receiver_id, content, False)
        msg.create()
    
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
        
    user_id = session['user_id']
    profiles = []
    profile_id = None
    profile_selected = None
    messages_data = []

    connections = Friendship.get_friendship_connections(user_id)

    if connections:
        other_user_ids = [
            conn.sender_id if conn.receiver_id == user_id else conn.receiver_id
            for conn in connections
        ]

        profiles = []
        for id in other_user_ids:
            profile = Profile._find_by_id(id)
            if profile:
                image_data = Profile.get_profile_image(profile.id)
                profiles.append({'id': profile.id, 'username': profile.username, 'image_data': image_data})

        last_message = Message.find_last_channel_id(user_id)
        
        if last_message:
            channel_id = last_message['channel_id']
            profile_id = last_message['profile_id']

            profile_selected = Profile._find_by_id(profile_id)

            # Récupérer les messages entre user_id et profile_id
            messages = Message.find_messages_by_channel_id(channel_id)
            if messages:
                messages_data = [{"receiver_id": msg.receiver_id, "sender_id": msg.sender_id, "content": msg.content,
                                  "created_at": msg.created_at.strftime('%Y-%m-%d %H:%M')} for msg in messages]
        else:
            channel = Channel.find_last_channel_by_user_id(user_id)
            if channel.user_a == user_id:
                profile_id = channel.user_b
            else:
                profile_id = channel.user_a
            profile_selected = Profile._find_by_id(profile_id)

    return render_template('chat.html', profiles=profiles, user_id=user_id, profile_selected=profile_selected,
                           profile_id=profile_id, messages_data=messages_data)

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
